import React, { useState, useEffect } from 'react';
import {
  Dialog, DialogTitle, DialogContent, DialogActions,
  TextField, Button, Grid, IconButton
} from '@mui/material';
import CloseIcon from '@mui/icons-material/Close';

const accentColor = '#1F1463';

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

    console.log('Updating referral:', payload); // Replace with actual API
    onUpdate(payload);
    onClose();
  };

  if (!formData) return null;

  return (
    <Dialog open={open} onClose={onClose} maxWidth="md" fullWidth>
      <DialogTitle sx={{ color: accentColor, fontSize: '1.25rem', fontWeight: 600 }}>
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
                value={value}
                fullWidth
                variant="outlined"
                size="small"
                onChange={handleChange(key)}
                sx={{
                  '& label': { color: accentColor },
                  '& .MuiOutlinedInput-root': {
                    borderRadius: 2,
                  },
                }}
              />
            </Grid>
          ))}
        </Grid>
      </DialogContent>

      <DialogActions sx={{ px: 3, pb: 2 }}>
        <Button
          onClick={onClose}
          variant="outlined"
          sx={{
            borderColor: accentColor,
            color: accentColor,
            '&:hover': {
              backgroundColor: '#f0f0ff',
              borderColor: accentColor
            }
          }}
        >
          Cancel
        </Button>
        <Button
          onClick={handleSubmit}
          variant="contained"
          sx={{
            backgroundColor: accentColor,
            '&:hover': {
              backgroundColor: '#2e1d91'
            }
          }}
        >
          Save
        </Button>
      </DialogActions>
    </Dialog>
  );
};

export default EditReferralModal;
