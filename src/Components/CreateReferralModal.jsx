// CreateReferralModal.jsx
import React, { useState } from 'react';
import {
  Dialog, DialogTitle, DialogContent, DialogActions,
  TextField, Button, Grid, IconButton
} from '@mui/material';
import CloseIcon from '@mui/icons-material/Close';

const CreateReferralModal = ({ open, onClose, onAdd }) => {
  const [formData, setFormData] = useState({
    serviceCategory: '',
    agency: '',
    referralProcess: '',
    hours: '',
    address: '',
    city: '',
    state: '',
    zipcode: '',
    phone: '',
    eligibilityRequirements: '',
    serviceAvailability: '',
    source: '',
    additionalInformation: '',
    serviceAreaZipCodes: ['']
  });

  const handleChange = (field) => (event) => {
    setFormData({ ...formData, [field]: event.target.value });
  };

  const handleZipCodeChange = (index) => (event) => {
    const newZipCodes = [...formData.serviceAreaZipCodes];
    newZipCodes[index] = event.target.value;
    setFormData({ ...formData, serviceAreaZipCodes: newZipCodes });
  };

  const addZipCodeField = () => {
    setFormData({
      ...formData,
      serviceAreaZipCodes: [...formData.serviceAreaZipCodes, '']
    });
  };

  const isAddDisabled = !(formData.serviceCategory && formData.agency);

  const handleSubmit = () => {
    const payload = {
      action: 'createReferral',
      data: {
        'Client Name': formData.agency,
        'Service Area Zip Code': formData.serviceAreaZipCodes[0],
        Phone: formData.phone,
        Email: formData.source
      }
    };
    // Replace with actual API call
    console.log('Submitting:', payload);
    onAdd(payload);
    onClose();
  };

  return (
    <Dialog open={open} onClose={onClose} maxWidth="md" fullWidth>
      <DialogTitle>
        Add New Referral
        <IconButton
          aria-label="close"
          onClick={onClose}
          sx={{ position: 'absolute', right: 8, top: 8 }}
        >
          <CloseIcon />
        </IconButton>
      </DialogTitle>
      <DialogContent dividers>
        <Grid container spacing={2}>
          {/* Service Category and Agency */}
          <Grid item xs={12} sm={6}>
            <TextField
              label="Service Category"
              fullWidth
              value={formData.serviceCategory}
              onChange={handleChange('serviceCategory')}
            />
          </Grid>
          <Grid item xs={12} sm={6}>
            <TextField
              label="Agency"
              fullWidth
              value={formData.agency}
              onChange={handleChange('agency')}
            />
          </Grid>
          {/* Referral Process and Hours */}
          <Grid item xs={12} sm={6}>
            <TextField
              label="Referral Process"
              fullWidth
              value={formData.referralProcess}
              onChange={handleChange('referralProcess')}
            />
          </Grid>
          <Grid item xs={12} sm={6}>
            <TextField
              label="Hours"
              fullWidth
              value={formData.hours}
              onChange={handleChange('hours')}
            />
          </Grid>
          {/* Address and City */}
          <Grid item xs={12} sm={6}>
            <TextField
              label="Address"
              fullWidth
              value={formData.address}
              onChange={handleChange('address')}
            />
          </Grid>
          <Grid item xs={12} sm={6}>
            <TextField
              label="City"
              fullWidth
              value={formData.city}
              onChange={handleChange('city')}
            />
          </Grid>
          {/* State and Zipcode */}
          <Grid item xs={12} sm={6}>
            <TextField
              label="State"
              fullWidth
              value={formData.state}
              onChange={handleChange('state')}
            />
          </Grid>
          <Grid item xs={12} sm={6}>
            <TextField
              label="Zipcode"
              fullWidth
              value={formData.zipcode}
              onChange={handleChange('zipcode')}
            />
          </Grid>
          {/* Phone and Eligibility Requirements */}
          <Grid item xs={12} sm={6}>
            <TextField
              label="Phone"
              fullWidth
              value={formData.phone}
              onChange={handleChange('phone')}
            />
          </Grid>
          <Grid item xs={12} sm={6}>
            <TextField
              label="Eligibility Requirements"
              fullWidth
              value={formData.eligibilityRequirements}
              onChange={handleChange('eligibilityRequirements')}
            />
          </Grid>
          {/* Service Availability and Source */}
          <Grid item xs={12} sm={6}>
            <TextField
              label="Service Availability"
              fullWidth
              value={formData.serviceAvailability}
              onChange={handleChange('serviceAvailability')}
            />
          </Grid>
          <Grid item xs={12} sm={6}>
            <TextField
              label="Source"
              fullWidth
              value={formData.source}
              onChange={handleChange('source')}
            />
          </Grid>
          {/* Additional Information */}
          <Grid item xs={12}>
            <TextField
              label="Additional Information"
              fullWidth
              multiline
              rows={4}
              value={formData.additionalInformation}
              onChange={handleChange('additionalInformation')}
            />
          </Grid>
          {/* Service Area Zip Codes */}
          <Grid item xs={12}>
            <Grid container spacing={1}>
              {formData.serviceAreaZipCodes.map((zip, index) => (
                <Grid item xs={12} sm={4} key={index}>
                  <TextField
                    label={`Zip code #${index + 1}`}
                    fullWidth
                    value={zip}
                    onChange={handleZipCodeChange(index)}
                  />
                </Grid>
              ))}
              <Grid item xs={12}>
                <Button onClick={addZipCodeField}>Add more</Button>
              </Grid>
            </Grid>
          </Grid>
        </Grid>
      </DialogContent>
      <DialogActions>
        <Button onClick={onClose}>Cancel</Button>
        <Button onClick={handleSubmit} disabled={isAddDisabled}>
          Add
        </Button>
      </DialogActions>
    </Dialog>
  );
};

export default CreateReferralModal;
