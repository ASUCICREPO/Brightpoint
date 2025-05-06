import React from 'react';
import {
  Dialog, DialogTitle, DialogContent, DialogActions,
  Typography, Button, Grid, IconButton
} from '@mui/material';
import CloseIcon from '@mui/icons-material/Close';

const ReferralDetailsModal = ({ open, onClose, referralData, onEdit, onDelete }) => {
  if (!open) return null;

  const hardcodedData = {
    name: "Planned Parenthood of Illinois",
    phone: "(309) 452-5737",
    address: "115 N. 1st St., Suite 200",
    city: "Springfield",
    state: "IL",
    zip: 62702,
    additionalInfo: "Medical Services",
    hours: "Hours vary by location; please contact for details",
    referralId: "efe83ac5-2226-41e0-bc00-026c73fa9a3f"
  };
  return (
    <Dialog open={open} onClose={onClose} maxWidth="md" fullWidth>
      <DialogTitle>
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
          <Grid item xs={6}>
            <Typography variant="subtitle2">Agency</Typography>
            <Typography variant="body1">{hardcodedData.name || hardcodedData["Client Name"]}</Typography>
          </Grid>
          <Grid item xs={6}>
            <Typography variant="subtitle2">Phone</Typography>
            <Typography variant="body1">{hardcodedData.phone || "N/A"}</Typography>
          </Grid>
          <Grid item xs={6}>
            <Typography variant="subtitle2">Address</Typography>
            <Typography variant="body1">{hardcodedData.address || "N/A"}</Typography>
          </Grid>
          <Grid item xs={6}>
            <Typography variant="subtitle2">City</Typography>
            <Typography variant="body1">{hardcodedData.city || "N/A"}</Typography>
          </Grid>
          <Grid item xs={6}>
            <Typography variant="subtitle2">State</Typography>
            <Typography variant="body1">{hardcodedData.state || "N/A"}</Typography>
          </Grid>
          <Grid item xs={6}>
            <Typography variant="subtitle2">Zip Code</Typography>
            <Typography variant="body1">{hardcodedData.zip || "N/A"}</Typography>
          </Grid>
          <Grid item xs={12}>
            <Typography variant="subtitle2">Service Category</Typography>
            <Typography variant="body1">{hardcodedData.additionInfo || "N/A"}</Typography>
          </Grid>
          <Grid item xs={12}>
            <Typography variant="subtitle2">Hours</Typography>
            <Typography variant="body1">{hardcodedData.hours || "N/A"}</Typography>
          </Grid>
        </Grid>
      </DialogContent>

      <DialogActions>
        <Button
          color="primary"
          onClick={() => onEdit(hardcodedData)}
        >
          Edit
        </Button>
        <Button
          color="error"
          onClick={() => onDelete(referralData.referral_id)}
        >
          Delete
        </Button>
      </DialogActions>
    </Dialog>
  );
};

export default ReferralDetailsModal;
