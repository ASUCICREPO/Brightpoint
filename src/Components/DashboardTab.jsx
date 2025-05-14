// DashboardTab.jsx
import {
  Box,
  Grid,
  Typography,
  Paper,
  FormControl,
  Select,
  MenuItem,
  InputLabel,
  Table,
  TableHead,
  TableRow,
  TableCell,
  TableBody,
} from '@mui/material';
import React, { useEffect, useRef, useState } from 'react';
import { ANALYTICS_API } from '../utilities/constants';
import { PieChart, Pie, Cell, Tooltip, Legend, ResponsiveContainer } from 'recharts';


const monthlyOptions = ["Last 3 Months", "Last 6 Months", "This Year", "All time"];
const zipCodeOptions = ["61701"]; // <- Replace with real options if dynamic

const DashboardTab = () => {
  const wsRef = useRef(null);
  const [faqData, setFaqData] = useState([]);
  const [perplexityData, setPerplexityData] = useState([]);
  const [totalUsers, setTotalUsers] = useState(0);
  const [totalReferrals, setTotalReferrals] = useState(0);
  const [feedbackStats, setFeedbackStats] = useState({ useful: 0, not_useful: 0, pending: 0, total: 0 });

  useEffect(() => {
    const fetchAnalytics = async () => {
      try {
        const response = await fetch(ANALYTICS_API, {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
          },
          body: JSON.stringify({
            start_date: "2025-01-01T00:00:00",
            end_date: "2025-04-28T23:59:59",
            zipcodes: ["61701"],
            limit: 10,
          }),
        });

        const data = await response.json();
        console.log("HTTPS API Response:", data);

        setFaqData(
          data.referral_counts?.map((item) => ({
            service: item.category,
            count: item.count,
          })) || []
        );

        setPerplexityData(data.perplexity_queries || []);
        setTotalUsers(data.user_count || 0);
        setTotalReferrals(data.total_queries || 0);
        setFeedbackStats(data.feedback_statistics || { useful: 0, not_useful: 0, pending: 0, total: 0 });


      } catch (error) {
        console.error("Error fetching analytics:", error);
      }
    };

    fetchAnalytics();
  }, []);
  const feedbackChartData = [
    { name: 'Useful', value: feedbackStats.useful },
    { name: 'Not Useful', value: feedbackStats.not_useful },
    { name: 'Pending', value: feedbackStats.pending },
  ];
  
  const FEEDBACK_COLORS = ['#4caf50', '#f44336', '#ff9800']; // green, red, orange
  
  const renderCustomLegend = (props) => {
    const { payload } = props;
    return (
      <ul style={{ listStyle: "none", paddingLeft: 0 }}>
        {payload.map((entry, index) => (
          <li key={`item-${index}`} style={{ color: entry.color, marginBottom: 4 }}>
            <span style={{ fontWeight: 500 }}>{entry.value}</span> ({entry.payload.value})
          </li>
        ))}
      </ul>
    );
  };

  return (
    <Box>
      {/* Filters */}
      <Grid container spacing={2} sx={{ mb: 2 }}>
        <Grid item xs={12} sm={6} md={4}>
          <FormControl fullWidth size="small">
            <InputLabel>Timeframe</InputLabel>
            <Select value="Last 3 Months" label="Monthly" sx={{ minWidth: 200 }}>
              {monthlyOptions.map((month, index) => (
                <MenuItem key={index} value={month}>{month}</MenuItem>
              ))}
            </Select>
          </FormControl>
        </Grid>
        <Grid item xs={12} sm={6} md={4}>
          <FormControl fullWidth size="small">
            <InputLabel>Filter by Zip Code</InputLabel>
            <Select
              multiple
              value={["61701"]}
              label="Filter by Zip Code"
              renderValue={(selected) => selected.join(', ')}
              sx={{ minWidth: 200 }}
            >
              {zipCodeOptions.map((zip, index) => (
                <MenuItem key={index} value={zip}>{zip}</MenuItem>
              ))}
            </Select>
          </FormControl>
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


      {/* FAQ */}
      {/* <Grid container spacing={2} mb={2}>
        <Grid item xs={12}> */}
          <Paper elevation={1} sx={{ p: 2, width: '100%' }}>
            <Typography variant="h6" fontWeight="bold" mb={2}>Frequently Asked Questions</Typography>
            <Table size="small">
              <TableHead>
                <TableRow>
                  <TableCell>Service Category</TableCell>
                  <TableCell align="right">Times asked</TableCell>
                </TableRow>
              </TableHead>
              <TableBody>
  {faqData.slice(0, 10).map((row, index) => (
    <TableRow key={index}>
      <TableCell>{row.service}</TableCell>
      <TableCell align="right">{row.count}</TableCell>
    </TableRow>
  ))}
</TableBody>
            </Table>
          </Paper>
        {/* </Grid>
      </Grid> */}

      <Paper elevation={1} sx={{ p: 2, mt: 2 }}>
  <Typography variant="h6" fontWeight="bold" mb={2}>Feedback Statistics</Typography>
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
      <Legend content={renderCustomLegend} />
    </PieChart>
  </ResponsiveContainer>
  <Typography variant="body2" textAlign="center" mt={2}>
    Total Feedback Received: <strong>{feedbackStats.total}</strong>
  </Typography>
</Paper>


      {/* Missed Referrals */}
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
