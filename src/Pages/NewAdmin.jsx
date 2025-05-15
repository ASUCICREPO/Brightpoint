import React, { useState } from 'react';
import {
  Box,
  Button,
  Typography,
  TextField,
  Alert
} from '@mui/material';
import { useNavigate } from 'react-router-dom';
import { signUp } from 'aws-amplify/auth';

const NewAdmin = () => {
  const [formData, setFormData] = useState({
    username: '',
    email: '',
    password: '',
    confirmPassword: ''
  });
  const [error, setError] = useState('');
  const [success, setSuccess] = useState('');
  const navigate = useNavigate();

  const handleChange = (field) => (e) =>
    setFormData({ ...formData, [field]: e.target.value });

  const handleCreateUser = async () => {
    const { username, email, password, confirmPassword } = formData;

    if (!username || !email || !password || !confirmPassword) {
      setError("Please fill all fields.");
      return;
    }

    if (password !== confirmPassword) {
      setError("Passwords do not match.");
      return;
    }

    try {
      // Use Amplify Auth.signUp for normal user sign up
      await signUp({
        username,
        password,
        options: {
          userAttributes: {
            email,
          },
        },
      });

      setSuccess("User created successfully! Please check your email to confirm your account.");
      setError('');
      // Optionally navigate to login or confirmation page after a delay
      setTimeout(() => navigate('/admin'), 4000);
    } catch (err) {
      console.error("Error creating user:", err);
      setError(err.message || "Failed to create user.");
      setSuccess('');
    }
  };

  return (
    <Box
      height="100vh"
      display="flex"
      justifyContent="center"
      alignItems="center"
      bgcolor="white"
    >
      <Box
        width="100%"
        maxWidth="400px"
        bgcolor="white"
        p={4}
        borderRadius={4}
        boxShadow={3}
        display="flex"
        flexDirection="column"
        alignItems="center"
      >
        <Typography variant="h5" fontWeight="bold" color="#1F1463" mb={2}>
          Create New Admin
        </Typography>

        {error && <Alert severity="error" sx={{ mb: 2 }}>{error}</Alert>}
        {success && <Alert severity="success" sx={{ mb: 2 }}>{success}</Alert>}

        {['username', 'email', 'password', 'confirmPassword'].map((field, index) => (
          <TextField
            key={index}
            label={field === 'confirmPassword' ? 'Confirm Password' : field.charAt(0).toUpperCase() + field.slice(1)}
            type={field.includes('password') ? 'password' : 'text'}
            value={formData[field]}
            onChange={handleChange(field)}
            margin="normal"
            fullWidth
            sx={{
              backgroundColor: '#f0f0f0',
              borderRadius: '12px',
              '& .MuiOutlinedInput-root': {
                borderRadius: '12px',
              },
            }}
          />
        ))}

        <Button
          variant="contained"
          onClick={handleCreateUser}
          fullWidth
          sx={{
            mt: 2,
            borderRadius: '20px',
            backgroundColor: '#1F1463',
            '&:hover': {
              backgroundColor: '#3724AD',
            },
          }}
        >
          Create Admin
        </Button>
      </Box>
    </Box>
  );
};

export default NewAdmin;
