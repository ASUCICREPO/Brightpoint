import React from 'react';
import {
  Dialog, DialogTitle, DialogContent, DialogActions,
  Typography, Button, Grid, IconButton, Box
} from '@mui/material';
import CloseIcon from '@mui/icons-material/Close';

const accentColor = '#1F1463';

const ReferralDetailsModal = ({ open, onClose, referralData, onEdit, onDelete }) => {
  if (!open) return null;

  const data = referralData || {};

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

  return (
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
            {renderField('Agency', data.name || data["Client Name"])}
          </Grid>
          <Grid item xs={12} sm={6}>
            {renderField('Phone', data.phone)}
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
            {renderField('Zip Code', data.zip)}
          </Grid>
          <Grid item xs={12} sm={6}>
            {renderField('Service Category', data.additionalInfo)}
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
          onClick={() => onDelete(referralData.referral_id)}
        >
          Delete
        </Button>
      </DialogActions>
    </Dialog>
  );
};

export default ReferralDetailsModal;
