import {
  Box,
  Grid,
  Typography,
  Paper,
  FormControl,
  Select,
  MenuItem,
  InputLabel,
  Chip,
  OutlinedInput,
  Table,
  TableHead,
  TableRow,
  TableCell,
  TableBody,
  Button,
} from '@mui/material';
import React, { useEffect, useRef, useState } from 'react';
import { ANALYTICS_API, REFERRAL_MANAGEMENT_API } from '../utilities/constants';
import { PieChart, Pie, Cell, Tooltip, Legend, ResponsiveContainer } from 'recharts';
import dayjs from 'dayjs'; // Add dayjs for date manipulation

const ITEM_HEIGHT = 48;
const ITEM_PADDING_TOP = 8;
const MenuProps = {
  PaperProps: {
    style: {
      maxHeight: ITEM_HEIGHT * 4.5 + ITEM_PADDING_TOP,
      width: 250,
    },
  },
};


const monthlyOptions = ["Last 3 Months", "Last 6 Months", "This Year", "All time"];

const DashboardTab = () => {
  const [faqData, setFaqData] = useState([]);
  const [perplexityData, setPerplexityData] = useState([]);
  const [totalUsers, setTotalUsers] = useState(0);
  const [totalReferrals, setTotalReferrals] = useState(0);
  const [feedbackStats, setFeedbackStats] = useState({ useful: 0, not_useful: 0, pending: 0, total: 0 });
  const [zipcodes, setZipcodes] = useState([]);
  const [selectedZipcodes, setSelectedZipcodes] = useState(['61701']);

  const [selectedTimeframe, setSelectedTimeframe] = useState("Last 3 Months");

  const ws = useRef(null);

  // Function to get zipcodes once and set options & default selection
  const zipcodeGetter = () => {
    ws.current = new WebSocket(REFERRAL_MANAGEMENT_API);

    ws.current.onopen = () => {
      console.log('WebSocket opened - requesting referrals');
      ws.current.send(JSON.stringify({ action: 'getReferrals' }));
    };

    ws.current.onmessage = (event) => {
      const response = JSON.parse(event.data);
      const referrals = response.referrals || [];

      const zipCodesSet = new Set();

      referrals.forEach((item) => {
        const zip = item['Service Area Zip Code'] || 'N/A';
        if (zip !== 'N/A') zipCodesSet.add(zip);
      });

      const zipArray = Array.from(zipCodesSet);

      setZipcodes(zipArray);

      // If the default zipcode is in the options, select it; else select none
      setSelectedZipcodes(zipArray); // Select all zipcodes by default

    };

    ws.current.onerror = (error) => console.error('WebSocket Error:', error);
    ws.current.onclose = () => console.log('WebSocket connection closed');
  };

  // Run zipcodeGetter once on mount
  useEffect(() => {
    zipcodeGetter();

    // Clean up websocket on unmount
    return () => {
      if (ws.current) {
        console.log('Closing WebSocket');
        ws.current.close();
      }
    };
  }, []);

  const getDateRange = (timeframe) => {
    const end = dayjs().endOf('day'); // today until end of day
    let start;

    switch(timeframe) {
      case "Last 3 Months":
        start = end.subtract(3, 'month').startOf('day');
        break;
      case "Last 6 Months":
        start = end.subtract(6, 'month').startOf('day');
        break;
      case "This Year":
        start = dayjs().startOf('year');
        break;
      case "All time":
        start = dayjs('2000-01-01'); // arbitrarily far past
        break;
      default:
        start = end.subtract(3, 'month').startOf('day');
    }

    return {
      start_date: start.toISOString(),
      end_date: end.toISOString(),
    };
  };


  // Whenever selectedZipcodes changes, fetch analytics from API
  useEffect(() => {
    // if (selectedZipcodes.length === 0) return;

    const { start_date, end_date } = getDateRange(selectedTimeframe);

    const fetchAnalytics = async () => {
      const { start_date, end_date } = getDateRange(selectedTimeframe);
    
      // Format zipcodes exactly as an array of strings
      const zipcodesFormatted = selectedZipcodes.map(zip => String(zip));
    
      const requestBody = {
        start_date,
        end_date,
        zipcodes: zipcodesFormatted,   // e.g. ["61701", "61822"]
        limit: 10,
        include_query_frequency: true,
        include_user_referrals: true,
        include_feedback_stats: true,
        include_perplexity_queries: true,
      };
    
      console.log("Fetching analytics with request:", requestBody);
    
      try {
        const response = await fetch(ANALYTICS_API, {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify(requestBody),
        });
    
        const data = await response.json();
    
        console.log("Received response:", data);
    
        setFaqData(data.query_frequency?.map(item => ({
          service: item.query,
          count: item.count,
        })) || []);
        setPerplexityData(data.perplexity_queries || []);
        setTotalUsers(data.user_count || 0);
        setTotalReferrals(data.referral_counts?.length || 0);
        setFeedbackStats(data.feedback_statistics || { useful: 0, not_useful: 0, pending: 0, total: 0 });
    
      } catch (error) {
        console.error("Error fetching analytics:", error);
      }
    };
    

    fetchAnalytics();
  }, [selectedZipcodes, selectedTimeframe]);

  const feedbackChartData = [
    { name: 'Useful', value: feedbackStats.useful },
    { name: 'Not Useful', value: feedbackStats.not_useful },
    { name: 'Pending', value: feedbackStats.pending },
  ];

  const FEEDBACK_COLORS = ['#4caf50', '#f44336', '#ff9800'];

  // Handler to clear all selected zipcodes
  const handleClearZipcodes = () => {
    setSelectedZipcodes([]);
  };

  return (
    <Box>
      {/* Filters */}
      <Grid container spacing={2} sx={{ mb: 2 }}>
        <Grid item xs={12} sm={6} md={4}>
          <FormControl fullWidth size="small">
            <InputLabel>Timeframe</InputLabel>
            <Select
                value={selectedTimeframe}
                onChange={(e) => setSelectedTimeframe(e.target.value)}
                label="Timeframe"
                sx={{ minWidth: 200 }}
              >

              {monthlyOptions.map((month, index) => (
                <MenuItem key={index} value={month}>{month}</MenuItem>
              ))}
            </Select>
          </FormControl>
        </Grid>

        <Grid item xs={12} sm={6} md={4}>
          <FormControl fullWidth size="small" sx={{maxWidth:300}} >
            <InputLabel>Filter by Zip Code</InputLabel>
            <Select
              multiple
              value={selectedZipcodes}
              onChange={(e) => setSelectedZipcodes(e.target.value)}
              input={<OutlinedInput label="Filter by Zip Code" />}
              renderValue={(selected) => (
                <Box sx={{ display: 'flex', flexWrap: 'wrap', gap: 0.5 }}>
                  {selected.map((value) => (
                    <Chip key={value} label={value} />
                  ))}
                </Box>
              )}
              MenuProps={MenuProps}
            >
              {zipcodes.map((zip, index) => (
                <MenuItem key={index} value={zip}>
                  {zip}
                </MenuItem>
              ))}
            </Select>
          </FormControl>
          <Button onClick={handleClearZipcodes} sx={{ mt: 1 }} size="small" variant="outlined">
            Clear All Zipcodes
          </Button>
        </Grid>
      </Grid>

      {/* Overview */}
      <Paper elevation={1} sx={{ p: 2, mb: 2 }}>
        <Typography variant="h6" fontWeight="bold" mb={2}>Overview</Typography>
        <Grid container spacing={2} justifyContent="center" textAlign="center">
          <Grid item xs={12} sm={6} md={3}>
            <Typography color="textSecondary">Total Users</Typography>
            <Typography variant="h4" color="primary">{totalUsers}</Typography>
          </Grid>
          <Grid item xs={12} sm={6} md={3}>
            <Typography color="textSecondary">Referrals Given</Typography>
            <Typography variant="h4" color="primary">{totalReferrals}</Typography>
          </Grid>
        </Grid>
      </Paper>

      {/* FAQ Table */}
      <Paper elevation={1} sx={{ p: 2, width: '100%' }}>
        <Typography variant="h6" fontWeight="bold" mb={2}>Frequently Asked Questions</Typography>
        <Table size="small">
          <TableHead>
            <TableRow>
              <TableCell fontWeight="bold">Question asked</TableCell>
              <TableCell align="right" fontWeight="bold">Times asked</TableCell>
            </TableRow>
          </TableHead>
          <TableBody>
            {faqData.map((row, index) => (
              <TableRow key={index}>
                <TableCell>{row.service}</TableCell>
                <TableCell align="right">{row.count}</TableCell>
              </TableRow>
            ))}
          </TableBody>
        </Table>
      </Paper>

      {/* Feedback Pie Chart */}
      <Paper elevation={1} sx={{ p: 2, mt: 2 }}>
        <Typography variant="h6" fontWeight="bold" mb={2}>Referral Feedback Statistics</Typography>
        <ResponsiveContainer width="100%" height={300}>
          <PieChart>
            <Pie
              data={feedbackChartData}
              dataKey="value"
              nameKey="name"
              cx="50%"
              cy="50%"
              outerRadius={100}
              label
            >
              {feedbackChartData.map((entry, index) => (
                <Cell key={`cell-${index}`} fill={FEEDBACK_COLORS[index % FEEDBACK_COLORS.length]} />
              ))}
            </Pie>
            <Tooltip />
            <Legend />
          </PieChart>
        </ResponsiveContainer>
        <Typography variant="body2" textAlign="center" mt={2}>
          Total Feedback Received: <strong>{feedbackStats.total}</strong>
        </Typography>
      </Paper>

      {/* Missed Referrals Table */}
      <Paper elevation={1} sx={{ p: 2 }}>
        <Typography variant="h6" fontWeight="bold" mb={2}>Missed Referrals</Typography>
        <Box sx={{ overflowX: 'auto' }}>
          <Table size="small">
            <TableHead>
              <TableRow>
                <TableCell>Query</TableCell>
                <TableCell>Translated Query</TableCell>
                <TableCell>Language</TableCell>
                <TableCell>Zipcode</TableCell>
                <TableCell>Timestamp</TableCell>
              </TableRow>
            </TableHead>
            <TableBody>
              {perplexityData.map((row, index) => (
                <TableRow key={index}>
                  <TableCell>{row.original_query}</TableCell>
                  <TableCell>{row.english_query}</TableCell>
                  <TableCell>{row.language}</TableCell>
                  <TableCell>{row.zipcode}</TableCell>
                  <TableCell>{new Date(row.timestamp).toLocaleString()}</TableCell>
                </TableRow>
              ))}
            </TableBody>
          </Table>
        </Box>
      </Paper>
    </Box>
  );
};

export default DashboardTab;
