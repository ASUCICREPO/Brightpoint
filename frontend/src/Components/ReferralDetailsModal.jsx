import React, { useState } from 'react';
import {
  Dialog, DialogTitle, DialogContent, DialogActions,
  Typography, Button, Grid, IconButton, Box
} from '@mui/material';
import CloseIcon from '@mui/icons-material/Close';

const accentColor = '#1F1463';

const ReferralDetailsModal = ({ open, onClose, referralData, onEdit, onDelete }) => {
  const [confirmOpen, setConfirmOpen] = useState(false);

  if (!open) return null;

  const data = referralData || {};
  console.log('ReferralDetailsModal data:', data);

  const renderField = (label, value) => (
    <Box
      sx={{
        borderRadius: 2,
        p: 2,
        border: '1px solid #e0e0e0',
        backgroundColor: '#fafafa'
      }}
    >
      <Typography variant="body1" sx={{ color: accentColor, fontWeight: 500 }}>
        {label}
      </Typography>
      <Typography variant="body2" sx={{ mt: 0.5 }}>
        {value || 'N/A'}
      </Typography>
    </Box>
  );

  const handleDeleteClick = () => {
    setConfirmOpen(true);
  };

  const handleConfirmDelete = () => {
    setConfirmOpen(false);
    onDelete(data.referral_id);
  };

  const handleCancelDelete = () => {
    setConfirmOpen(false);
  };

  return (
    <>
      <Dialog open={open} onClose={onClose} maxWidth="md" fullWidth>
        <DialogTitle sx={{ color: accentColor, fontSize: '1.25rem', fontWeight: 600 }}>
          Referral Details
          <IconButton
            onClick={onClose}
            sx={{ position: 'absolute', right: 8, top: 8 }}
          >
            <CloseIcon />
          </IconButton>
        </DialogTitle>

        <DialogContent dividers>
          <Grid container spacing={2}>
            <Grid item xs={12} sm={6}>
              {renderField('Agency', data.agency)}
            </Grid>
            <Grid item xs={12} sm={6}>
              {renderField('Phone', data.process)}  
            </Grid>
            <Grid item xs={12} sm={6}>
              {renderField('Address', data.address)}
            </Grid>
            <Grid item xs={12} sm={6}>
              {renderField('City', data.city)} 
            </Grid>
            <Grid item xs={12} sm={6}>
              {renderField('State', data.state)} 
            </Grid>
            <Grid item xs={12} sm={6}>
              {renderField('Zip Code', data.zipcode)} 
            </Grid>
            <Grid item xs={12} sm={6}>
              {renderField('Service Category', data.category)}
            </Grid>
            <Grid item xs={12} sm={6}>
              {renderField('Hours', data.hours)}
            </Grid>
          </Grid>
        </DialogContent>

        <DialogActions sx={{ px: 3, pb: 2 }}>
          <Button
            onClick={() => onEdit(data)}
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
            Edit
          </Button>
          <Button
            color="error"
            variant="outlined"
            onClick={handleDeleteClick}
          >
            Delete
          </Button>
        </DialogActions>
      </Dialog>

      {/* Confirmation Dialog */}
      <Dialog open={confirmOpen} onClose={handleCancelDelete} maxWidth="xs" fullWidth>
        <DialogTitle sx={{ color: accentColor, fontWeight: 600 }}>
          Confirm Deletion
        </DialogTitle>
        <DialogContent dividers>
          <Typography>
            Are you sure you want to delete this referral? This action cannot be undone.
          </Typography>
        </DialogContent>
        <DialogActions>
          <Button onClick={handleCancelDelete} variant="outlined">
            Cancel
          </Button>
          <Button onClick={handleConfirmDelete} color="error" variant="contained">
            Delete
          </Button>
        </DialogActions>
      </Dialog>
    </>
  );
};

export default ReferralDetailsModal;
