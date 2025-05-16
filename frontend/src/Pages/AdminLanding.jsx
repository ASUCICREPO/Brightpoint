import React, { useState, useEffect } from 'react';
import {
  Box,
  Button,
  Typography,
  TextField,
  InputAdornment,
  IconButton
} from '@mui/material';
import { Visibility, VisibilityOff } from '@mui/icons-material';
import { useNavigate } from 'react-router-dom';
import BrightpointLogo from '../Assets/Brightpoint_logo.svg';
import { useUser } from '../utilities/UserContext';
import { handleReferralOnLogin } from "../utilities/userReferralHandler";
import * as AmplifyAuth from 'aws-amplify/auth';

const AdminLanding = () => {
  const { updateUser } = useUser();
  const [username, setUsername] = useState('');
  const [password, setPassword] = useState('');
  const [showPassword, setShowPassword] = useState(false);
  const navigate = useNavigate();
  const zipcode = "62701";

  useEffect(() => {
    const logoutPreviousUser = async () => {
      try {
        await AmplifyAuth.signOut();
        console.log("Previous user logged out successfully.");
      } catch (error) {
        console.error("Error signing out the previous user:", error.message || error);
      }
    };

    logoutPreviousUser();
  }, []);

  const handleLogin = async () => {
    try {
      const response = await AmplifyAuth.signIn({ username, password });
      console.log('Cognito login success:', response);
  
      if (!response.isSignedIn) {
        const step = response.nextStep?.signInStep;
        
        if (step === 'CONFIRM_SIGN_UP') {
          alert("Please confirm your account before logging in.");
          // Optionally navigate to confirmation page or handle confirmation here
          return;
        }
  
        alert("Login incomplete: " + step);
        return;
      }
  
      const session = await AmplifyAuth.fetchAuthSession();
  
      // ✅ getAccessToken now works because user is fully signed in
      const payload = session.tokens?.accessToken?.payload;
      const groups = payload?.["cognito:groups"];
      const userGroups = Array.isArray(groups) ? groups : groups ? [groups] : [];
  
      console.log('User groups:', userGroups);
  
      if (!userGroups.includes("Admin")) {
        alert("Access denied: You are not authorized to access this admin portal.");
        await AmplifyAuth.signOut();
        return;
      }
  
      updateUser({ username: username, zipcode });
  
      handleReferralOnLogin(username, (referrals) => {
        if (referrals?.length) {
          updateUser({ referrals });
          console.log('Referrals updated in user context:', referrals);
        } else {
          console.error('Error: No referral data returned');
        }
      });
  
      navigate('/admindashboard');
  
    } catch (error) {
      console.error('Cognito login error:', error.message || error);
      alert('Login failed: ' + (error.message || 'Unknown error'));
    }
  };
  
  const isButtonDisabled = !username || !password;

  return (
    <Box height="100vh" display="flex" flexDirection="column" justifyContent="center" alignItems="center" bgcolor="white">
      <img src={BrightpointLogo} alt="Brightpoint Logo" height="50" style={{ marginBottom: 10 }} />

      <Box
        width="40%"
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

        <Button
          variant="contained"
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
      {/* <Typography variant="body2" mt={2}>
  <a href="/newadmin" style={{ color: '#1F1463', textDecoration: 'underline' }}>
    Create new Admin
  </a>
</Typography> */}

    </Box>
  );
};

export default AdminLanding;
