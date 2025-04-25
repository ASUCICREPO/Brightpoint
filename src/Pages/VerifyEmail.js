import React, { useState } from 'react';
import { Box, Typography, TextField, Button, Snackbar, Alert } from '@mui/material';
import { confirmSignUp } from 'aws-amplify/auth'; // ⬅️ Cognito confirm

const VerifyEmail = () => {
  const [code, setCode] = useState('');
  const [snackbarOpen, setSnackbarOpen] = useState(false);
  const [message, setMessage] = useState('');
  const [severity, setSeverity] = useState('success');

  const handleConfirm = async () => {
    try {
      const { isSignUpComplete } = await confirmSignUp({
        username: 'your-username-here', // Replace with userData.username or prop/context
        confirmationCode: code,
      });

      if (isSignUpComplete) {
        setMessage("Email confirmed! You can now log in.");
        setSeverity('success');
        setSnackbarOpen(true);
      }
    } catch (err) {
      setMessage(err.message || "Verification failed.");
      setSeverity('error');
      setSnackbarOpen(true);
    }
  };

  return (
    <Box textAlign="center" mt={10}>
      <Typography variant="h4" mb={2}>Verify Your Email</Typography>
      <TextField
        label="Verification Code"
        value={code}
        onChange={(e) => setCode(e.target.value)}
        fullWidth
        margin="normal"
      />
      <Button variant="contained" onClick={handleConfirm}>Verify</Button>

      <Snackbar open={snackbarOpen} autoHideDuration={3000} onClose={() => setSnackbarOpen(false)}>
        <Alert severity={severity}>{message}</Alert>
      </Snackbar>
    </Box>
  );
};

export default VerifyEmail;
