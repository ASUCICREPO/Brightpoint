import React, { useState, useEffect } from 'react';
import { Box, Button, Typography, TextField, Link, InputAdornment, IconButton, Alert, Snackbar } from '@mui/material';
import { Visibility, VisibilityOff } from '@mui/icons-material';
import { useNavigate } from 'react-router-dom';
import BrightpointLogo from '../Assets/Brightpoint_logo.svg';
import { useUser } from '../utilities/UserContext';
import { handleReferralOnLogin } from "../utilities/userReferralHandler";
import { signIn, signOut } from 'aws-amplify/auth';
import { fetchAndStoreUserData } from '../utilities/handleLogin';

const LandingPage = ({ setOpenModal }) => {
  const { updateUser, fetchUserWithFeedback, isLoading: contextLoading } = useUser();

  const [username, setUsername] = useState('');
  const [password, setPassword] = useState('');
  const [showPassword, setShowPassword] = useState(false);
  const [isLoading, setIsLoading] = useState(false);
  const [errorMessage, setErrorMessage] = useState('');
  const [showError, setShowError] = useState(false);
  const navigate = useNavigate();

  // Clear session storage on component mount
  useEffect(() => {
    sessionStorage.removeItem('feedbackModalDismissed');
  }, []);

  // Log out previous user when page loads
  useEffect(() => {
    const logoutPreviousUser = async () => {
      try {
        await signOut();
      } catch (error) {
        console.error("Error signing out previous user:", error.message || error);
      }
    };
    logoutPreviousUser();
  }, []);

  // Show error popup
  const showErrorPopup = (message) => {
    setErrorMessage(message);
    setShowError(true);
  };

  // Hide error popup
  const hideErrorPopup = () => {
    setShowError(false);
    setErrorMessage('');
  };

  // Main login function with error handling
  const handleLogin = async () => {
    setIsLoading(true);
    hideErrorPopup();

    try {
      // Clean and validate input
      const cleanUsername = username.trim();

      if (!cleanUsername) {
        throw new Error("Please enter your username");
      }

      if (!password) {
        throw new Error("Please enter your password");
      }

      // Attempt Cognito authentication
      const user = await signIn({ username: cleanUsername, password });


      // Clear session flags for fresh login
      sessionStorage.removeItem('feedbackModalDismissed');

      // Fetch user data
      await fetchAndStoreUserData(cleanUsername, updateUser);

      let userDataWithFeedback = null;

      // Fetch feedback questions and determine language
      try {
        userDataWithFeedback = await fetchUserWithFeedback(cleanUsername, 'english');
      } catch (feedbackError) {
        console.error("Error fetching feedback questions:", feedbackError);
        // Don't block login if feedback fetch fails
      }

      // Determine navigation path based on language
      const lang = userDataWithFeedback?.language || 'english';
      let langPath = '/app';

      if (lang.toLowerCase() === 'spanish') {
        langPath = '/esapp';
      } else if (lang.toLowerCase() === 'polish') {
        langPath = '/plapp';
      }

      navigate(langPath);


    } catch (error) {
      console.error('Login error:', error);

      // Handle specific error types with user-friendly messages
      let userMessage = '';

      switch (error.name) {
        case 'UserNotFoundException':
          userMessage = `User "${username.trim()}" does not exist. Please check your username or contact support.`;
          break;

        case 'NotAuthorizedException':
          userMessage = 'Incorrect username or password. Please try again.';
          break;

        case 'UserNotConfirmedException':
          userMessage = 'Your account is not confirmed. Please check your email for a verification link.';
          break;

        case 'PasswordResetRequiredException':
          userMessage = 'A password reset is required for your account. Please reset your password.';
          break;

        case 'TooManyRequestsException':
          userMessage = 'Too many failed login attempts. Please wait a few minutes before trying again.';
          break;

        case 'UserStatusException':
          userMessage = 'Your account is disabled or inactive. Please contact support.';
          break;

        case 'InvalidParameterException':
          userMessage = 'Invalid login information provided. Please check your username and password.';
          break;

        case 'ResourceNotFoundException':
          userMessage = 'Login service is not available. Please contact support.';
          break;

        case 'NetworkError':
          userMessage = 'Network connection error. Please check your internet connection and try again.';
          break;

        default:
          if (error.message && error.message.includes('User does not exist')) {
            userMessage = `User "${username.trim()}" does not exist. Please check your username.`;
          } else if (error.message && error.message.includes('Incorrect username or password')) {
            userMessage = 'Incorrect username or password. Please try again.';
          } else if (error.message && error.message.includes('network')) {
            userMessage = 'Network connection error. Please check your internet connection.';
          } else {
            userMessage = error.message || 'An unexpected error occurred. Please try again.';
          }
      }

      showErrorPopup(userMessage);

    } finally {
      setIsLoading(false);
    }
  };

  // Handle Enter key press
  const handleKeyPress = (event) => {
    if (event.key === 'Enter' && !isButtonDisabled) {
      handleLogin();
    }
  };

  const isButtonDisabled = !username || !password || isLoading || contextLoading;

  return (
    <Box height="100vh" display="flex" flexDirection="column" justifyContent="center" alignItems="center" bgcolor="white">

      {/* Logo */}
      <img src={BrightpointLogo} alt="Brightpoint Logo" height="6%" style={{ marginBottom: 10 }} />

      {/* Main Login Form */}
      <Box
        width="30%"
        maxWidth="40%"
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

        {/* Username Field */}
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
          onKeyPress={handleKeyPress}
          disabled={isLoading || contextLoading}
          error={showError && errorMessage.includes('username')}
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
          onKeyPress={handleKeyPress}
          disabled={isLoading || contextLoading}
          error={showError && errorMessage.includes('password')}
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
                <IconButton
                  onClick={() => setShowPassword(!showPassword)}
                  edge="end"
                  disabled={isLoading || contextLoading}
                >
                  {showPassword ? <VisibilityOff /> : <Visibility />}
                </IconButton>
              </InputAdornment>
            ),
          }}
        />

        {/* Login Button */}
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
          {isLoading ? "Logging in..." : contextLoading ? "Loading..." : "Log In"}
        </Button>

        {/* Loading Indicator */}
        {(isLoading || contextLoading) && (
          <Typography variant="caption" sx={{ mt: 1, color: 'gray', textAlign: 'center' }}>
            {isLoading ? "Authenticating..." : "Fetching your data..."}
          </Typography>
        )}
      </Box>

      {/* Sign Up Link */}
      <Box mt={2}>
        <Typography variant="body2">
          Don't have an account?{' '}
          <Link href="/newsignup" color="#0000FF">
            Sign Up
          </Link>
          {' '}to create an account
        </Typography>
      </Box>

      {/* Error Popup/Snackbar */}
      <Snackbar
        open={showError}
        autoHideDuration={6000}
        onClose={hideErrorPopup}
        anchorOrigin={{ vertical: 'top', horizontal: 'center' }}
      >
        <Alert
          onClose={hideErrorPopup}
          severity="error"
          sx={{
            width: '100%',
            maxWidth: '500px',
            fontSize: '14px'
          }}
          variant="filled"
        >
          {errorMessage}
        </Alert>
      </Snackbar>

      {/* Development Debug Info (minimal) */}
      {process.env.NODE_ENV === 'development' && (
        <Box
          sx={{
            position: 'fixed',
            bottom: '10px',
            right: '10px',
            background: 'rgba(0,0,0,0.1)',
            padding: '8px',
            borderRadius: '4px',
            fontSize: '10px',
            color: '#666'
          }}
        >
          Dev: {isLoading ? 'Loading' : 'Ready'}
        </Box>
      )}
    </Box>
  );
};

export default LandingPage;