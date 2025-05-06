import React, { useEffect, useState } from 'react';
import {
  Box,
  Typography,
  Paper,
  TextField,
  MenuItem,
  InputAdornment,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  Checkbox,
  IconButton,
  TablePagination,
  Grid, Button, 
} from "@mui/material";
import SearchIcon from "@mui/icons-material/Search";
import AddIcon from "@mui/icons-material/Add";
import { REFERRAL_MANAGEMENT_API } from '../utilities/constants';
import CreateReferralModal from './CreateReferralModal';
import ReferralDetailsModal from './ReferralDetailsModal';
import EditReferralModal from './EditReferralModal';

export default function ReferralDatabase() {
  const [agencies, setAgencies] = useState([]);
  const [categories, setCategories] = useState([]);
  const [cities, setCities] = useState([]);
  const [zipcodes, setZipcodes] = useState([]);
  const [rows, setRows] = useState([]);
  const [selectedReferral, setSelectedReferral] = useState(null); // Now holds referralId
  const [createModalOpen, setCreateModalOpen] = useState(false);
  const [detailsModalOpen, setDetailsModalOpen] = useState(false);
  const [editModalOpen, setEditModalOpen] = useState(false);
  const [searchQuery, setSearchQuery] = useState('');

  useEffect(() => {
    const socket = new WebSocket(REFERRAL_MANAGEMENT_API);

    socket.onopen = () => {
      const getAllMsg = { action: "getReferrals" };
      socket.send(JSON.stringify(getAllMsg));
    };

    socket.onmessage = (event) => {
      const response = JSON.parse(event.data);
      const referrals = response.referrals;
    
      const agenciesSet = new Set();
      const categoriesSet = new Set();
      const citiesSet = new Set();
      const zipCodesSet = new Set();
      const structuredReferrals = [];
    
      referrals.forEach(item => {
        const name = item["Organization"] || item["Client Name"];
        
        // ✅ Filter out entries that don't start with "PATH"
        if (!name || !name.startsWith("Planned")) return;
    
        const phone = item.Phone;
        const address = item.Address || "N/A";
        const city = item.City || "N/A";
        const zip = item["Service Area Zip Code"] || "N/A";
        const additionalInfo = item["Service Category Type"] || "N/A";
        const referralId = item.referral_id;
        const state = item["State"];
        const hours = item["Hours"];
    
        agenciesSet.add(name);
        if (additionalInfo) categoriesSet.add(additionalInfo);
        if (city) citiesSet.add(city);
        if (zip !== "N/A") zipCodesSet.add(zip);
    
        structuredReferrals.push({
          name,
          phone,
          address,
          city,
          zip,
          additionalInfo,
          referralId: referralId || null,
          state,
          hours,
        });
      });
    
      setAgencies(Array.from(agenciesSet));
      setCategories(Array.from(categoriesSet));
      setCities(Array.from(citiesSet));
      setZipcodes(Array.from(zipCodesSet));
    
      const formattedRows = structuredReferrals.map((referral) => ({
        agency: referral.name,
        category: referral.additionalInfo,
        process: referral.phone,
        hours: referral.hours,
        address: referral.address,
        city: referral.city,
        state: referral.state,
        zipcode: referral.zip,
        fullData: referral,
        referralId: referral.referral_id,
      }));
    
      setRows(formattedRows);
    };
    

    socket.onerror = (error) => {
      console.error('WebSocket Error: ', error);
    };

    socket.onclose = () => {
      console.log('WebSocket connection closed');
    };

    return () => {
      socket.close();
    };
  }, []);
  useEffect(() => {
    console.log("detailsModalOpen changed:", detailsModalOpen);
  }, [detailsModalOpen]);
  

  // New handleClick function to trigger the modal
  const handleClick = (referral) => {
    console.log("Referral clicked:", referral);  // Check if it's logging
    setDetailsModalOpen(true); // Open the modal
    // setSelectedReferral(referral); // Store the full referral data
    // detailsModalOpen = true;
    console.log(detailsModalOpen);
  };


  return (
    <Box>
      <Typography variant="h4" fontWeight="bold" mb={2} color="primary">
        Providers
      </Typography>

      <Paper elevation={1} sx={{ p: 2 }}>
        <Grid container spacing={2} alignItems="center" mb={2}>
          <Grid item xs={12} md={2}>
          <TextField
  fullWidth
  variant="outlined"
  placeholder="Search Keyword"
  value={searchQuery}
  onChange={(e) => setSearchQuery(e.target.value)}
  InputProps={{
    startAdornment: (
      <InputAdornment position="start">
        <SearchIcon />
      </InputAdornment>
    )
  }}
/>

          </Grid>
          <Grid item xs={12} md={2} width={200}>
            <TextField select fullWidth label="Search Agency">
              {agencies.map((agency) => (
                <MenuItem key={agency} value={agency}>{agency}</MenuItem>
              ))}
            </TextField>
          </Grid>
          <Grid item xs={12} md={2} width={200}>
            <TextField select fullWidth label="Search Category">
              {categories.map((cat) => (
                <MenuItem key={cat} value={cat}>{cat}</MenuItem>
              ))}
            </TextField>
          </Grid>
          <Grid item xs={12} md={2} width={200}>
            <TextField select fullWidth label="Search City">
              {cities.map((city) => (
                <MenuItem key={city} value={city}>{city}</MenuItem>
              ))}
            </TextField>
          </Grid>
          <Grid item xs={12} md={2} width={200}>
            <TextField select fullWidth label="Search Zipcode">
              {zipcodes.map((zip) => (
                <MenuItem key={zip} value={zip}>{zip}</MenuItem>
              ))}
            </TextField>
          </Grid>
          <Grid item xs={12} md={1}>
            <IconButton sx={{ bgcolor: "primary.main", color: "white" }} onClick={() => setCreateModalOpen(true)}>
              <AddIcon />
            </IconButton>
          </Grid>
        </Grid>

        <TableContainer sx={{ overflowX: "auto" }}>
          <Table stickyHeader>
            <TableHead>
              <TableRow>
                <TableCell> </TableCell>
                <TableCell>Agency</TableCell>
                <TableCell>Service Category</TableCell>
                <TableCell>Referral Process</TableCell>
                <TableCell>Hours</TableCell>
                <TableCell>Address</TableCell>
                <TableCell>City</TableCell>
                <TableCell>State</TableCell>
                <TableCell>Zipcode</TableCell>
              </TableRow>
            </TableHead>
            <TableBody>
              {rows.map((row, i) => (
                <TableRow key={i}>
                  <TableCell>
                    <Button
                      variant="contained"
                      size="small"
                      onClick={() => handleClick(row.fullData)}// Use the handleClick function
                    >
                      View
                    </Button>
                  </TableCell>
                  <TableCell>{row.agency}</TableCell>
                  <TableCell>{row.category}</TableCell>
                  <TableCell>{row.process}</TableCell>
                  <TableCell>{row.hours}</TableCell>
                  <TableCell>{row.address}</TableCell>
                  <TableCell>{row.city}</TableCell>
                  <TableCell>{row.state}</TableCell>
                  <TableCell>{row.zipcode}</TableCell>
                </TableRow>
              ))}
            </TableBody>
          </Table>
        </TableContainer>

        <Box mt={2}>
          <TablePagination
            rowsPerPageOptions={[10, 25, 50]}
            component="div"
            count={1300}
            rowsPerPage={10}
            page={0}
            onPageChange={() => {}}
            onRowsPerPageChange={() => {}}
          />
        </Box>
      </Paper>

      <CreateReferralModal
        open={createModalOpen}
        onClose={() => setCreateModalOpen(false)}
        onSubmit={(data) => console.log("Create Referral Data:", data)}
      />

{detailsModalOpen && (
  <ReferralDetailsModal
    open={detailsModalOpen}
    onClose={() => setDetailsModalOpen(false)}
    // referral={selectedReferral.fullData}
  />
)}


      <EditReferralModal
        open={editModalOpen}
        onClose={() => setEditModalOpen(false)}
        referralData={selectedReferral} // Pass the full data for editing
        onUpdate={(data) => console.log("Updated Referral:", data)}
      />
    </Box>
  );
}
