import React, { useState } from 'react';
import {
  Dialog, DialogTitle, DialogContent, DialogActions,
  TextField, Button, Grid, IconButton, Typography
} from '@mui/material';
import CloseIcon from '@mui/icons-material/Close';

const ACCENT_COLOR = '#1F1463';

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
    console.log('Submitting:', payload);
    onAdd(payload);
    onClose();
  };

  const renderField = (label, value, onChange, multiline = false) => (
    <>
      <Typography variant="body1" sx={{ color: ACCENT_COLOR, mb: 0.5 }}>{label}</Typography>
      <TextField
        fullWidth
        multiline={multiline}
        rows={multiline ? 4 : 1}
        value={value}
        onChange={onChange}
        variant="outlined"
        sx={{
          borderRadius: 2,
          '& .MuiOutlinedInput-root': {
            borderRadius: 2,
            '&.Mui-focused fieldset': {
              borderColor: ACCENT_COLOR
            }
          },
          '& label.Mui-focused': {
            color: ACCENT_COLOR
          }
        }}
      />
    </>
  );

  return (
    <Dialog open={open} onClose={onClose} maxWidth="md" fullWidth>
      <DialogTitle sx={{ color: ACCENT_COLOR, fontSize: '1.5rem', fontWeight: 'bold' }}>
        Add New Referral
        <IconButton
          aria-label="close"
          onClick={onClose}
          sx={{ position: 'absolute', right: 8, top: 8, color: ACCENT_COLOR }}
        >
          <CloseIcon />
        </IconButton>
      </DialogTitle>

      <DialogContent dividers>
        <Grid container spacing={2}>
          <Grid item xs={12} sm={6}>{renderField("Service Category", formData.serviceCategory, handleChange('serviceCategory'))}</Grid>
          <Grid item xs={12} sm={6}>{renderField("Agency", formData.agency, handleChange('agency'))}</Grid>
          <Grid item xs={12} sm={6}>{renderField("Referral Process", formData.referralProcess, handleChange('referralProcess'))}</Grid>
          <Grid item xs={12} sm={6}>{renderField("Hours", formData.hours, handleChange('hours'))}</Grid>
          <Grid item xs={12} sm={6}>{renderField("Address", formData.address, handleChange('address'))}</Grid>
          <Grid item xs={12} sm={6}>{renderField("City", formData.city, handleChange('city'))}</Grid>
          <Grid item xs={12} sm={6}>{renderField("State", formData.state, handleChange('state'))}</Grid>
          <Grid item xs={12} sm={6}>{renderField("Zipcode", formData.zipcode, handleChange('zipcode'))}</Grid>
          <Grid item xs={12} sm={6}>{renderField("Phone", formData.phone, handleChange('phone'))}</Grid>
          <Grid item xs={12} sm={6}>{renderField("Eligibility Requirements", formData.eligibilityRequirements, handleChange('eligibilityRequirements'))}</Grid>
          <Grid item xs={12} sm={6}>{renderField("Service Availability", formData.serviceAvailability, handleChange('serviceAvailability'))}</Grid>
          <Grid item xs={12} sm={6}>{renderField("Source", formData.source, handleChange('source'))}</Grid>
          <Grid item xs={12}>{renderField("Additional Information", formData.additionalInformation, handleChange('additionalInformation'), true)}</Grid>

          {/* Service Area Zip Codes */}
          <Grid item xs={12}>
            <Typography variant="body1" sx={{ color: ACCENT_COLOR, mb: 1 }}>
              Service Area Zip Codes
            </Typography>
            <Grid container spacing={1}>
              {formData.serviceAreaZipCodes.map((zip, index) => (
                <Grid item xs={12} sm={4} key={index}>
                  <TextField
                    fullWidth
                    value={zip}
                    label={`Zip code #${index + 1}`}
                    onChange={handleZipCodeChange(index)}
                    sx={{
                      '& .MuiOutlinedInput-root': {
                        borderRadius: 2,
                        '&.Mui-focused fieldset': {
                          borderColor: ACCENT_COLOR
                        }
                      },
                      '& label.Mui-focused': {
                        color: ACCENT_COLOR
                      }
                    }}
                  />
                </Grid>
              ))}
              <Grid item xs={12}>
                <Button onClick={addZipCodeField} sx={{ color: ACCENT_COLOR, textTransform: 'none' }}>
                  Add more
                </Button>
              </Grid>
            </Grid>
          </Grid>
        </Grid>
      </DialogContent>

      <DialogActions>
        <Button onClick={onClose} sx={{ color: ACCENT_COLOR }}>Cancel</Button>
        <Button
          onClick={handleSubmit}
          disabled={isAddDisabled}
          variant="contained"
          sx={{
            backgroundColor: ACCENT_COLOR,
            '&:hover': {
              backgroundColor: '#150f4e'
            }
          }}
        >
          Add
        </Button>
      </DialogActions>
    </Dialog>
  );
};

export default CreateReferralModal;
