import React, { useState } from 'react';
import { Box, Button, Typography, TextField, Link, InputAdornment, IconButton } from '@mui/material';
import { Visibility, VisibilityOff } from '@mui/icons-material';
import { useNavigate } from 'react-router-dom';
import BrightpointLogo from '../Assets/Brightpoint_logo.svg';
import { useUser } from '../utilities/UserContext'; // Import UserContext
import { handleReferralOnLogin } from "../utilities/userReferralHandler"; // Import the referral handler
import { signIn } from 'aws-amplify/auth'; // Correct import for Auth

const LandingPage = () => {
  const { updateUser } = useUser(); // Get updateUser function from context
  const [username, setUsername] = useState('');
  const [password, setPassword] = useState('');
  const [showPassword, setShowPassword] = useState(false);
  const navigate = useNavigate();
  const zipcode = "62701"; // Hardcoded zipcode for this example

  const handleLogin = async () => {
    try {
      // Authenticate using Cognito
      const user = await signIn({ username, password });
      console.log('Cognito login success:', user);

      updateUser({ username, zipcode });

      // Handle referrals
      handleReferralOnLogin(username, (referrals) => {
        if (referrals && referrals.length > 0) {
          updateUser({ referrals });
          console.log('Referrals updated in user context:', referrals);
        } else {
          console.error('Error: No referral data returned');
        }
      });

      navigate('/referralapp'); // Navigate to the next page

    } catch (error) {
      console.error('Cognito login error:', error.message || error);
      alert('Login failed: ' + (error.message || 'Unknown error'));
    }
  };

  const isButtonDisabled = !username || !password;

  return (
    <Box height="100vh" display="flex" flexDirection="column" justifyContent="center" alignItems="center" bgcolor="white">
      
      {/* Logo above the container */}
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
          Log In
        </Typography>

        {/* Username Label */}
        <Typography variant="body1" alignSelf="flex-start" mb={0.5}>
          Username:
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

        {/* Password Label */}
        <Typography variant="body1" alignSelf="flex-start" mt={2} mb={0.5}>
          Password:
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

        {/* Log In Button */}
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
          onClick={handleLogin}
        >
          Log In
        </Button>
      </Box>

      {/* Sign Up Text outside the box */}
      <Box mt={2}>
        <Typography variant="body2">
          Don’t have an account?{' '}
          <Link href="/newsignup" color="#0000FF">
            Sign Up
          </Link>
          {' '}to create an account
        </Typography>
      </Box>

    </Box>
  );
};

export default LandingPage;
