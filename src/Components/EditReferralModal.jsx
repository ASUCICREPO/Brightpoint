// EditReferralModal.jsx
import React, { useState, useEffect } from 'react';
import {
  Dialog, DialogTitle, DialogContent, DialogActions,
  TextField, Button, Grid, IconButton
} from '@mui/material';
import CloseIcon from '@mui/icons-material/Close';

const EditReferralModal = ({ open, onClose, referralData, onUpdate }) => {
  const [formData, setFormData] = useState({ ...referralData });

  useEffect(() => {
    if (referralData) {
      setFormData({ ...referralData });
    }
  }, [referralData]);

  const handleChange = (field) => (event) => {
    setFormData({ ...formData, [field]: event.target.value });
  };

  const handleSubmit = () => {
    const payload = {
      action: 'editReferral',
      data: formData,
    };

    // Replace with actual API call
    console.log('Updating referral:', payload);
    onUpdate(payload);
    onClose();
  };

  if (!formData) return null;

  return (
    <Dialog open={open} onClose={onClose} maxWidth="md" fullWidth>
      <DialogTitle>
        Edit Referral
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
          {Object.entries(formData).map(([key, value]) => (
            <Grid item xs={12} sm={6} key={key}>
              <TextField
                label={key}
                fullWidth
                value={value}
                onChange={handleChange(key)}
              />
            </Grid>
          ))}
        </Grid>
      </DialogContent>
      <DialogActions>
        <Button onClick={onClose}>Cancel</Button>
        <Button onClick={handleSubmit}>Save</Button>
      </DialogActions>
    </Dialog>
  );
};

export default EditReferralModal;
