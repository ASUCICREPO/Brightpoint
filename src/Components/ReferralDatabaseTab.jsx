import React, { useEffect, useState } from 'react';
import {
  Box, Typography, Paper, TextField, InputAdornment, Table, TableBody, TableCell,
  TableContainer, TableHead, TableRow, IconButton, TablePagination, Grid, Chip, OutlinedInput,
  FormControl, InputLabel, Select, MenuItem
} from "@mui/material";
import SearchIcon from "@mui/icons-material/Search";
import AddIcon from "@mui/icons-material/Add";
import { useTheme } from '@mui/material/styles';
import { REFERRAL_MANAGEMENT_API } from '../utilities/constants';
import CreateReferralModal from './CreateReferralModal';
import ReferralDetailsModal from './ReferralDetailsModal';
import EditReferralModal from './EditReferralModal';

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

function getStyles(name, selectedValues, theme) {
  return {
    fontWeight: selectedValues.includes(name)
      ? theme.typography.fontWeightMedium
      : theme.typography.fontWeightRegular,
  };
}

export default function ReferralDatabase() {
  const theme = useTheme();
  const [agencies, setAgencies] = useState([]);
  const [categories, setCategories] = useState([]);
  const [cities, setCities] = useState([]);
  const [zipcodes, setZipcodes] = useState([]);
  const [allRows, setAllRows] = useState([]);
  const [filteredRows, setFilteredRows] = useState([]);

  const [selectedReferral, setSelectedReferral] = useState(null);
  const [createModalOpen, setCreateModalOpen] = useState(false);
  const [detailsModalOpen, setDetailsModalOpen] = useState(false);
  const [editModalOpen, setEditModalOpen] = useState(false);

  const [searchQuery, setSearchQuery] = useState('');
  const [selectedAgencies, setSelectedAgencies] = useState([]);
  const [selectedCategories, setSelectedCategories] = useState([]);
  const [selectedCities, setSelectedCities] = useState([]);
  const [selectedZipcodes, setSelectedZipcodes] = useState([]);

  const [page, setPage] = useState(0);
  const [rowsPerPage, setRowsPerPage] = useState(10);

  useEffect(() => {
    const socket = new WebSocket(REFERRAL_MANAGEMENT_API);
    socket.onopen = () => socket.send(JSON.stringify({ action: "getReferrals" }));

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
        const phone = item.Phone;
        const address = item.Address || "N/A";
        const city = item.City || "N/A";
        const zip = item["Service Area Zip Code"] || "N/A";
        const category = item["Service Category Type"] || "N/A";
        const referral_id = item.referral_id;
        const state = item.State || "N/A";
        const hours = item.Hours || "N/A";

        agenciesSet.add(name);
        if (category) categoriesSet.add(category);
        if (city) citiesSet.add(city);
        if (zip !== "N/A") zipCodesSet.add(zip);

        structuredReferrals.push({
          agency: name,
          category,
          process: phone,
          hours,
          address,
          city,
          state,
          zipcode: zip,
          fullData: item,
          referral_id,
        });
      });

      setAgencies(Array.from(agenciesSet));
      setCategories(Array.from(categoriesSet));
      setCities(Array.from(citiesSet));
      setZipcodes(Array.from(zipCodesSet));
      setAllRows(structuredReferrals);
    };

    socket.onerror = (error) => console.error('WebSocket Error: ', error);
    socket.onclose = () => console.log('WebSocket connection closed');
    return () => socket.close();
  }, []);

  useEffect(() => {
    let filtered = allRows;

    if (searchQuery)
      filtered = filtered.filter(row =>
        Object.values(row).some(value =>
          typeof value === 'string' &&
          value.toLowerCase().includes(searchQuery.toLowerCase())
        )
      );

    if (selectedAgencies.length)
      filtered = filtered.filter(row => selectedAgencies.includes(row.agency));

    if (selectedCategories.length)
      filtered = filtered.filter(row => selectedCategories.includes(row.category));

    if (selectedCities.length)
      filtered = filtered.filter(row => selectedCities.includes(row.city));

    if (selectedZipcodes.length)
      filtered = filtered.filter(row => selectedZipcodes.includes(row.zipcode));

    setFilteredRows(filtered);
    setPage(0);
  }, [searchQuery, selectedAgencies, selectedCategories, selectedCities, selectedZipcodes, allRows]);

  const handleClick = (referral) => {
    setSelectedReferral(referral);
    setDetailsModalOpen(true);
  };

  return (
    <Box>
      <Typography variant="h4" fontWeight="bold" mb={2} color="primary">Providers</Typography>
      <Paper elevation={1} sx={{ p: 2 }}>
        <Grid container spacing={2} alignItems="center" mb={2}>
          <Grid item xs={12} md={3}>
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

          {[{
            label: 'Agency',
            value: selectedAgencies,
            setter: setSelectedAgencies,
            options: agencies
          }, {
            label: 'Category',
            value: selectedCategories,
            setter: setSelectedCategories,
            options: categories
          }, {
            label: 'City',
            value: selectedCities,
            setter: setSelectedCities,
            options: cities
          }, {
            label: 'Zipcode',
            value: selectedZipcodes,
            setter: setSelectedZipcodes,
            options: zipcodes
          }].map(({ label, value, setter, options }) => (
            <Grid item xs={12} md={2} key={label} width={200}>
              <FormControl fullWidth>
                <InputLabel>{label}</InputLabel>
                <Select
                  multiple
                  value={value}
                  onChange={(e) => setter(typeof e.target.value === 'string' ? e.target.value.split(',') : e.target.value)}
                  input={<OutlinedInput label={label} />}
                  renderValue={(selected) => (
                    <Box sx={{ display: 'flex', flexWrap: 'wrap', gap: 0.5 }}>
                      {selected.map((val) => <Chip key={val} label={val} />)}
                    </Box>
                  )}
                  MenuProps={MenuProps}
                >
                  {options.map((opt) => (
                    <MenuItem key={opt} value={opt} style={getStyles(opt, value, theme)}>
                      {opt}
                    </MenuItem>
                  ))}
                </Select>
              </FormControl>
            </Grid>
          ))}

          <Grid item xs={12} md={1}>
            <IconButton
              sx={{ bgcolor: "primary.main", color: "white" }}
              onClick={() => setCreateModalOpen(true)}
            >
              <AddIcon />
            </IconButton>
          </Grid>
        </Grid>

        <TableContainer>
          <Table stickyHeader>
            <TableHead>
              <TableRow>
                <TableCell>Agency</TableCell>
                <TableCell>Category</TableCell>
                <TableCell>City</TableCell>
                <TableCell>Zipcode</TableCell>
                <TableCell>Phone</TableCell>
              </TableRow>
            </TableHead>
            <TableBody>
              {filteredRows.slice(page * rowsPerPage, page * rowsPerPage + rowsPerPage).map((row, index) => (
                <TableRow key={index} hover onClick={() => handleClick(row)} sx={{ cursor: 'pointer' }}>
                  <TableCell>{row.agency}</TableCell>
                  <TableCell>{row.category}</TableCell>
                  <TableCell>{row.city}</TableCell>
                  <TableCell>{row.zipcode}</TableCell>
                  <TableCell>{row.process}</TableCell>
                </TableRow>
              ))}
            </TableBody>
          </Table>
        </TableContainer>

        <TablePagination
          rowsPerPageOptions={[10]}
          component="div"
          count={filteredRows.length}
          rowsPerPage={rowsPerPage}
          page={page}
          onPageChange={(_, newPage) => setPage(newPage)}
        />
      </Paper>

      <CreateReferralModal open={createModalOpen} onClose={() => setCreateModalOpen(false)} />
      <ReferralDetailsModal open={detailsModalOpen} onClose={() => setDetailsModalOpen(false)} referral={selectedReferral} />
      <EditReferralModal open={editModalOpen} onClose={() => setEditModalOpen(false)} referral={selectedReferral} />
    </Box>
  );
}
