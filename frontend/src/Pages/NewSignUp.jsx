import React, { useState, useEffect } from 'react';
import {
  Box, Button, Typography, TextField, Link, InputAdornment, IconButton
} from '@mui/material';
import { Visibility, VisibilityOff } from '@mui/icons-material';
import { useNavigate } from 'react-router-dom';
import BrightpointLogo from '../Assets/Brightpoint_logo.svg';
import { useUser } from '../utilities/UserContext';
import { signOut } from 'aws-amplify/auth';

const NewSignUp = () => {
  const { updateUser } = useUser();
  const [username, setUsername] = useState('');
  const [email, setEmail] = useState(''); // ✅ Add email field
  const [password, setPassword] = useState('');
  const [confirmPassword, setConfirmPassword] = useState('');
  const [showPassword, setShowPassword] = useState(false);
  const [showConfirmPassword, setShowConfirmPassword] = useState(false);
  const navigate = useNavigate();

  useEffect(() => {
    const logoutPreviousUser = async () => {
      try {
        await signOut();
        console.log("Previous user logged out successfully.");
      } catch (error) {
        console.error("Error signing out the previous user:", error.message || error);
      }
    };

    logoutPreviousUser();
  }, []);

  const handleSignUp = async () => {
    if (password !== confirmPassword) {
      alert("Passwords do not match!");
      return;
    }

    // ✅ Store all signup data in context for later use
    updateUser({
      username,
      email,
      password
    });

    console.log("Signup data stored in context:", { username, email });
    navigate('/newusersignup'); // Navigate to profile completion page
  };

  const isButtonDisabled = !username || !email || !password || !confirmPassword; // ✅ Include email

  return (
    <Box height="100vh" display="flex" flexDirection="column" justifyContent="center" alignItems="center" bgcolor="white">

      <img src={BrightpointLogo} alt="Brightpoint Logo" height="50" style={{ marginBottom: 10 }} />

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
        justifyContent="center"
      >
        <Typography variant="h4" color="#1F1463" gutterBottom fontWeight="bold">
          Sign Up
        </Typography>

        {/* Username Field */}
        <Typography variant="body1" alignSelf="flex-start" mb={0.5}>
          Username <span style={{ color: 'red' }}>*</span>
        </Typography>
        <TextField
          placeholder="Enter your username"
          variant="outlined"
          fullWidth
          margin="normal"
          value={username}
          onChange={(e) => setUsername(e.target.value)}
          sx={{
            backgroundColor: '#f0f0f0',
            borderRadius: '12px',
            '& .MuiOutlinedInput-root': {
              borderRadius: '12px',
            },
          }}
        />

        {/* ✅ Email Field */}
        <Typography variant="body1" alignSelf="flex-start" mt={2} mb={0.5}>
          Email <span style={{ color: 'red' }}>*</span>
        </Typography>
        <TextField
          placeholder="Enter your email"
          variant="outlined"
          fullWidth
          margin="normal"
          type="email"
          value={email}
          onChange={(e) => setEmail(e.target.value)}
          sx={{
            backgroundColor: '#f0f0f0',
            borderRadius: '12px',
            '& .MuiOutlinedInput-root': {
              borderRadius: '12px',
            },
          }}
        />

        {/* Password Field */}
        <Typography variant="body1" alignSelf="flex-start" mt={2} mb={0.5}>
          Password <span style={{ color: 'red' }}>*</span>
        </Typography>
        <TextField
          placeholder="Enter your password"
          variant="outlined"
          fullWidth
          margin="normal"
          type={showPassword ? 'text' : 'password'}
          value={password}
          onChange={(e) => setPassword(e.target.value)}
          sx={{
            backgroundColor: '#f0f0f0',
            borderRadius: '12px',
            '& .MuiOutlinedInput-root': {
              borderRadius: '12px',
            },
          }}
          InputProps={{
            endAdornment: (
              <InputAdornment position="end">
                <IconButton onClick={() => setShowPassword(!showPassword)} edge="end">
                  {showPassword ? <VisibilityOff /> : <Visibility />}
                </IconButton>
              </InputAdornment>
            ),
          }}
        />

        {/* Confirm Password Field */}
        <Typography variant="body1" alignSelf="flex-start" mt={2} mb={0.5}>
          Confirm Password <span style={{ color: 'red' }}>*</span>
        </Typography>
        <TextField
          placeholder="Re-enter your password"
          variant="outlined"
          fullWidth
          margin="normal"
          type={showConfirmPassword ? 'text' : 'password'}
          value={confirmPassword}
          onChange={(e) => setConfirmPassword(e.target.value)}
          sx={{
            backgroundColor: '#f0f0f0',
            borderRadius: '12px',
            '& .MuiOutlinedInput-root': {
              borderRadius: '12px',
            },
          }}
          InputProps={{
            endAdornment: (
              <InputAdornment position="end">
                <IconButton onClick={() => setShowConfirmPassword(!showConfirmPassword)} edge="end">
                  {showConfirmPassword ? <VisibilityOff /> : <Visibility />}
                </IconButton>
              </InputAdornment>
            ),
          }}
        />

        <Button
          variant="contained"
          color="error"
          fullWidth
          sx={{
            borderRadius: '20px',
            mt: 2,
            backgroundColor: isButtonDisabled ? '#cccccc' : '#1F1463',
            '&:hover': {
              backgroundColor: isButtonDisabled ? '#cccccc' : '#3724AD',
            },
          }}
          disabled={isButtonDisabled}
          onClick={handleSignUp}
        >
          Continue
        </Button>
      </Box>

      <Box mt={2}>
        <Typography variant="body2">
          Already registered?{' '}
          <Link href="/" color="#0000FF">
            Log In
          </Link> to your account
        </Typography>
      </Box>

    </Box>
  );
};

export default NewSignUp;