import React, { useState, useEffect } from 'react';
import { Box, Button, Typography, TextField, RadioGroup, FormControlLabel, Radio, Snackbar, Alert, Divider, IconButton } from '@mui/material';
import BrightpointLogo from '../Assets/Brightpoint_logo.svg';
import { DatePicker, LocalizationProvider } from '@mui/x-date-pickers';
import AddIcon from '@mui/icons-material/Add';
import { AdapterDateFns } from '@mui/x-date-pickers/AdapterDateFns';
import { useNavigate } from 'react-router-dom';
import { useUser } from '../utilities/UserContext';
import { signUp, confirmSignUp, resendSignUpCode } from 'aws-amplify/auth';
import { Amplify } from 'aws-amplify'; // ✅ Added missing import
import { USER_API, USER_ADD_API } from '../utilities/constants';

const NewUser = () => {
  const { userData, updateUser } = useUser();
  const [page, setPage] = useState(0);
  const totalPages = 4;

  // Form Data State
  const [formData, setFormData] = useState({
    givenName: '',
    lastName: '',
    zipcode: '',
    phonenumber: '',
    language: '',
    children: [{ birthDate: null }],
    dueDate: null,
  });

  // Verification state
  const [verificationCode, setVerificationCode] = useState('');
  const [isSignUpComplete, setIsSignUpComplete] = useState(false);

  // Snackbar State
  const [snackbarOpen, setSnackbarOpen] = useState(false);
  const [snackbarMessage, setSnackbarMessage] = useState('');

  const navigate = useNavigate();

  // ✅ COMPLETE COGNITO POOL VERIFICATION
  useEffect(() => {
    console.log("🔍 COGNITO POOL VERIFICATION:");
    console.log("=".repeat(50));

    // Check environment variables
    console.log("Environment Variables:");
    console.log("- REACT_APP_USER_POOL_ID:", process.env.REACT_APP_USER_POOL_ID);
    console.log("- REACT_APP_USER_POOL_CLIENT_ID:", process.env.REACT_APP_USER_POOL_CLIENT_ID);
    console.log("- REACT_APP_REGION:", process.env.REACT_APP_REGION);
    console.log("- REACT_APP_USER_ADD_API:", process.env.REACT_APP_USER_ADD_API);
    console.log("- REACT_APP_USER_API:", process.env.REACT_APP_USER_API);

    // Check Amplify configuration
    const config = Amplify.getConfig();
    console.log("Amplify Configuration:");
    console.log("- User Pool ID:", config.Auth?.Cognito?.userPoolId);
    console.log("- Client ID:", config.Auth?.Cognito?.userPoolClientId);
    console.log("- Region:", config.Auth?.Cognito?.region);

    // Verify it's YOUR pool (should be different from old wrong one)
    const poolId = config.Auth?.Cognito?.userPoolId;
    if (poolId) {
      console.log("✅ Pool Verification:");
      console.log(`- Pool ID: ${poolId}`);
      console.log(`- Is correct region: ${poolId.startsWith('us-east-1_') ? '✅ YES' : '❌ NO'}`);
      console.log(`- Is old wrong pool: ${poolId === 'us-east-1_umBuF7Dx8' ? '❌ YES (WRONG!)' : '✅ NO (GOOD!)'}`);

      if (poolId === 'us-east-1_umBuF7Dx8') {
        console.error("🚨 CRITICAL: Still using the WRONG Cognito pool!");
        console.error("🚨 This means environment variables are not being picked up correctly.");
      } else {
        console.log("🎉 SUCCESS: Using a different pool - likely the correct one!");
      }
    } else {
      console.error("❌ CRITICAL: No Cognito pool configured!");
    }

    // Check API URLs
    console.log("API URLs Verification:");
    console.log("- USER_ADD_API:", USER_ADD_API);
    console.log("- USER_API:", USER_API);
    console.log(`- Is using old hardcoded API: ${USER_ADD_API?.includes('f6mk2ph20e') ? '❌ YES (WRONG!)' : '✅ NO (GOOD!)'}`);

    console.log("=".repeat(50));
  }, []);

  const handleCompleteSignup = async () => {
    const { username, password, email } = userData;
    const { givenName, lastName, zipcode, phonenumber } = formData;

    console.log("🚀 STARTING COGNITO SIGNUP:");
    console.log("=".repeat(40));
    console.log("Signup credentials:", { username, password: "***", email });

    // ✅ VERIFY TARGET POOL RIGHT BEFORE SIGNUP
    const targetPool = Amplify.getConfig().Auth?.Cognito?.userPoolId;
    console.log("🎯 TARGET POOL ID:", targetPool);
    console.log("🔍 Is this your CDK pool?", targetPool !== 'us-east-1_umBuF7Dx8' ? '✅ YES' : '❌ NO - STILL WRONG!');

    try {
      const response = await signUp({
        username,
        password,
        options: {
          userAttributes: {
            email,
          },
        },
      });

      console.log("✅ COGNITO SIGNUP RESPONSE:");
      console.log("- User ID:", response.userId);
      console.log("- Is Sign Up Complete:", response.isSignUpComplete);
      console.log("- Next Step:", response.nextStep);
      console.log("- Full Response:", response);

      setIsSignUpComplete(true);
      setSnackbarMessage("Signup successful! Please check your email for verification code.");
      setSnackbarOpen(true);

      // Move to verification page
      setPage(3);

    } catch (error) {
      console.error("❌ COGNITO SIGNUP ERROR:");
      console.error("- Error message:", error.message);
      console.error("- Error code:", error.name);
      console.error("- Full error:", error);
      setSnackbarMessage(`Signup failed: ${error.message}`);
      setSnackbarOpen(true);
    }
    console.log("=".repeat(40));
  };

  const handleEmailVerification = async () => {
    const { username } = userData;

    console.log("🔐 STARTING EMAIL VERIFICATION:");
    console.log("- Username:", username);
    console.log("- Verification Code:", verificationCode);
    console.log("- Form Data:", formData);

    let isUserConfirmed = false;

    try {
      await confirmSignUp({
        username: username,
        confirmationCode: verificationCode
      });

      console.log("✅ Email verification successful");
      isUserConfirmed = true;

    } catch (error) {
      console.error("❌ VERIFICATION ERROR:");
      console.error("- Error message:", error.message);
      console.error("- Error name:", error.name);

      if (error.name === 'NotAuthorizedException' && error.message.includes('Current status is CONFIRMED')) {
        console.log("ℹ️ User is already confirmed, proceeding with profile save...");
        isUserConfirmed = true;
      } else if (error.name === 'CodeMismatchException') {
        setSnackbarMessage("Invalid verification code. Please try again.");
        setSnackbarOpen(true);
        return;
      } else if (error.name === 'ExpiredCodeException') {
        setSnackbarMessage("Verification code has expired. Please request a new one.");
        setSnackbarOpen(true);
        return;
      } else {
        console.error("- Full error:", error);
        setSnackbarMessage(`Verification failed: ${error.message}`);
        setSnackbarOpen(true);
        return;
      }
    }

    // If user is confirmed, proceed with REST API call
    if (isUserConfirmed) {
      try {
        // ✅ FIXED: Ensure consistent field mapping
        const restPayload = {
          user_id: username,
          Zipcode: formData.zipcode,
          Phone: formData.phonenumber,  // API expects "Phone"
          Email: userData.email,
          FirstName: formData.givenName,
          LastName: formData.lastName,
          Language: formData.language,
          operation: "PUT",
        };

        console.log("📤 SENDING TO REST API:");
        console.log("- URL:", USER_ADD_API);
        console.log("- Payload:", restPayload);

        // ✅ DEBUG: Show exactly what phone number we're sending
        console.log("🔍 PHONE NUMBER DEBUG:");
        console.log("- formData.phonenumber:", formData.phonenumber);
        console.log("- Payload.Phone:", restPayload.Phone);

        const restRes = await fetch(USER_ADD_API, {
          method: 'PUT',
          headers: {
            'Content-Type': 'application/json',
          },
          body: JSON.stringify(restPayload),
        });

        const restData = await restRes.json();

        if (!restRes.ok) {
          console.error("❌ REST API ERROR:");
          console.error("- Status:", restRes.status);
          console.error("- Response:", restData);
          throw new Error(`REST API call failed: ${restData.message || 'Unknown error'}`);
        }

        console.log("✅ REST API SUCCESS:");
        console.log("- Response:", restData);

        // ✅ UPDATE USER CONTEXT with complete profile data
        const completeUserData = {
          username: username,
          user_id: username,  // ✅ Fix: Set user_id to username
          email: userData.email,
          zipcode: formData.zipcode,
          phoneNumber: formData.phonenumber,  // ✅ Fix: Use camelCase for context
          Phone: formData.phonenumber,        // ✅ Also keep API format for compatibility
          firstName: formData.givenName,
          lastName: formData.lastName,
          language: formData.language,
        };

        console.log("🔄 UPDATING USER CONTEXT:");
        console.log("- Complete User Data:", completeUserData);

        updateUser(completeUserData);

        setSnackbarMessage("Account verified and profile saved successfully!");
        setSnackbarOpen(true);

        // Navigate to app after successful verification and profile save
        setTimeout(() => {
          navigate('/app');
        }, 2000);

      } catch (error) {
        console.error("❌ REST API ERROR:");
        console.error("- Error message:", error.message);
        console.error("- Full error:", error);
        setSnackbarMessage(`Profile save failed: ${error.message}`);
        setSnackbarOpen(true);
      }
    }
  };

  // ✅ OPTIONAL: Resend verification code function
  const handleResendCode = async () => {
    try {
      await resendSignUpCode({ username: userData.username });
      setSnackbarMessage("New verification code sent to your email!");
      setSnackbarOpen(true);
    } catch (error) {
      console.error("❌ RESEND CODE ERROR:", error);
      setSnackbarMessage(`Failed to resend code: ${error.message}`);
      setSnackbarOpen(true);
    }
  };

  const handleNext = () => {
    if (page === 2) {
      // Last form page - trigger signup
      handleCompleteSignup();
    } else if (page === 3) {
      // Verification page - verify email
      handleEmailVerification();
    } else {
      // Regular navigation
      setPage(page + 1);
    }
  };

  const handleBack = () => {
    if (page > 0) setPage(page - 1);
  };

  const handleChange = (field) => (event) => {
    const value = event.target.value;

    console.log(`Updating field: ${field}, New Value: ${value}`);

    setFormData((prev) => {
      const updatedForm = { ...prev, [field]: value };
      console.log("Updated formData:", updatedForm);
      return updatedForm;
    });

    if (field === 'zipcode') {
      updateUser({ ...userData, zipcode: value });
      console.log("User Context after zipCode update:", userData);
    }
  };

  // Fixed field mapping
  const getFieldName = (label) => {
    const fieldMap = {
      'First Name': 'givenName',
      'Last Name': 'lastName',
      'Zip Code': 'zipcode',
      'Phone Number': 'phonenumber'
    };
    return fieldMap[label] || label.toLowerCase().replace(' ', '');
  };

  const handleChildChange = (index, date) => {
    const newChildren = [...formData.children];
    newChildren[index].birthDate = date;
    setFormData({ ...formData, children: newChildren });
  };

  const addChild = () => {
    setFormData({
      ...formData,
      children: [...formData.children, { birthDate: null }],
    });
  };

  return (
    <Box height="100vh" display="flex" flexDirection="column" justifyContent="center" alignItems="center" bgcolor="white">

      {/* Snackbar */}
      <Snackbar
        open={snackbarOpen}
        autoHideDuration={4000}
        onClose={() => setSnackbarOpen(false)}
        anchorOrigin={{ vertical: 'top', horizontal: 'center' }}
      >
        <Alert
          severity={snackbarMessage.includes('failed') ? 'error' : 'success'}
          sx={{ backgroundColor: 'white', color: 'black', fontWeight: 'bold', boxShadow: 1 }}
        >
          {snackbarMessage}
        </Alert>
      </Snackbar>

      {/* Logo */}
      <img src={BrightpointLogo} alt="Brightpoint Logo" height="60" style={{ marginBottom: 10 }} />

      {/* Container */}
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
        {/* Progress Indicator */}
        <Box display="flex" justifyContent="center" gap={2} width="100%" mb={3}>
          {[...Array(totalPages)].map((_, index) => (
            <Box
              key={index}
              flex={1}
              height={8}
              borderRadius={4}
              bgcolor={index <= page ? 'primary.main' : 'grey.400'}
            />
          ))}
        </Box>

        <Typography variant="h5" color="#1F1463" gutterBottom fontWeight="bold">
          {page === 3 ? 'Verify Email' : 'Welcome!'}
        </Typography>

        {/* Page 0: First Name, Last Name, Zip Code */}
        {page === 0 && (
          <>
            {['First Name', 'Last Name', 'Zip Code'].map((label, index) => (
              <Box key={index} width="100%" mb={2}>
                <Typography variant="body1" alignSelf="flex-start" mb={0.5}>
                  {label} <span style={{ color: 'red' }}>*</span>
                </Typography>
                <TextField
                  placeholder={`Enter your ${label.toLowerCase()}`}
                  variant="outlined"
                  fullWidth
                  value={formData[getFieldName(label)]}
                  onChange={handleChange(getFieldName(label))}
                  sx={{
                    backgroundColor: '#f0f0f0',
                    borderRadius: '8px',
                    '& .MuiOutlinedInput-root': {
                      borderRadius: '8px',
                    },
                  }}
                />
              </Box>
            ))}
          </>
        )}

        {/* Page 1: Phone, Preferred Language */}
        {page === 1 && (
          <>
            <Box width="100%" mb={2}>
              <Typography variant="body1" alignSelf="flex-start" mb={0.5}>
                Phone Number
              </Typography>
              <TextField
                placeholder="Enter your phone number"
                variant="outlined"
                fullWidth
                value={formData.phonenumber}
                onChange={handleChange('phonenumber')}
                sx={{
                  backgroundColor: '#f0f0f0',
                  borderRadius: '8px',
                  '& .MuiOutlinedInput-root': {
                    borderRadius: '8px',
                  },
                }}
              />
            </Box>

            {/* Preferred Language Radio Group */}
            <Box width="100%" mt={2}>
              <Typography variant="body1" alignSelf="flex-start" mb={1}>
                Preferred Language:
              </Typography>
              <RadioGroup row value={formData.language} onChange={handleChange('language')}>
                {['English', 'Spanish', 'Polish'].map((lang) => (
                  <FormControlLabel
                    key={lang}
                    value={lang}
                    control={<Radio />}
                    label={lang}
                    sx={{
                      flex: 1,
                      textAlign: 'center',
                      border: '2px solid',
                      borderColor: 'primary.main',
                      borderRadius: '50px',
                      p: 0,
                      mx: 1,
                      transition: '0.3s',
                      backgroundColor: formData.language === lang ? 'rgba(31, 20, 99, 0.1)' : 'transparent',
                      color: formData.language === lang ? 'black' : 'black',
                      '&:hover': { backgroundColor: 'rgba(31, 20, 99, 0.1)' },
                    }}
                  />
                ))}
              </RadioGroup>
            </Box>
          </>
        )}

        {/* Page 2: Add Child Info */}
        {page === 2 && (
          <>
            <Typography variant="h5" color="#1F1463" gutterBottom fontWeight="bold">
              Add Child Info
            </Typography>

            {formData.children.map((child, index) => (
              <Box key={index} width="100%" mb={2}>
                <Typography variant="body1" alignSelf="flex-start" mb={0.5}>
                  Birth Date of Child #{index + 1}
                </Typography>
                <LocalizationProvider dateAdapter={AdapterDateFns}>
                  <Box width="100%" display="flex" flexDirection="column">
                    <DatePicker
                      value={child.birthDate}
                      onChange={(date) => handleChildChange(index, date)}
                      renderInput={(params) => <TextField {...params} fullWidth />}
                    />
                  </Box>
                </LocalizationProvider>
              </Box>
            ))}

            {/* Add Another Child Button */}
            <Box width="100%" mb={2}>
              <IconButton onClick={addChild} sx={{ color: 'primary.main' }}>
                <AddIcon />
              </IconButton>
              <Typography variant="body1" display="inline" sx={{ color: 'primary.main' }}>
                Add another child
              </Typography>
            </Box>

            <Divider sx={{ width: '100%', marginBottom: 2 }} />

            {/* Expected Due Date */}
            <Box width="100%" mb={2}>
              <Typography variant="body1" alignSelf="flex-start" mb={0.5}>
                Expected Due Date
              </Typography>
              <LocalizationProvider dateAdapter={AdapterDateFns}>
                <Box width="100%" display="flex" flexDirection="column">
                  <DatePicker
                    value={formData.dueDate}
                    onChange={(date) => setFormData({ ...formData, dueDate: date })}
                    renderInput={(params) => <TextField {...params} fullWidth />}
                  />
                </Box>
              </LocalizationProvider>
            </Box>
          </>
        )}

        {/* Page 3: Email Verification */}
        {page === 3 && (
          <>
            <Typography variant="body1" textAlign="center" mb={2}>
              We sent a verification code to<br />
              <strong>{userData?.email}</strong>
            </Typography>

            <Box width="100%" mb={2}>
              <Typography variant="body1" alignSelf="flex-start" mb={0.5}>
                Verification Code <span style={{ color: 'red' }}>*</span>
              </Typography>
              <TextField
                placeholder="Enter 6-digit code"
                variant="outlined"
                fullWidth
                value={verificationCode}
                onChange={(e) => setVerificationCode(e.target.value)}
                sx={{
                  backgroundColor: '#f0f0f0',
                  borderRadius: '8px',
                  '& .MuiOutlinedInput-root': {
                    borderRadius: '8px',
                  },
                }}
              />
            </Box>

            {/* Resend Code Button */}
            <Box width="100%" mb={2} textAlign="center">
              <Button
                variant="text"
                onClick={handleResendCode}
                sx={{
                  color: 'primary.main',
                  textTransform: 'none',
                  fontSize: '0.9rem'
                }}
              >
                Didn't receive code? Resend
              </Button>
            </Box>
          </>
        )}

        {/* Navigation Buttons */}
        <Box display="flex" width="100%" mt={3} gap={2}>
          {page > 0 && page < 3 && (
            <Button
              variant="outlined"
              fullWidth
              sx={{
                borderRadius: '20px',
                borderColor: 'primary.main',
                color: 'primary.main',
                backgroundColor: 'white',
                '&:hover': {
                  backgroundColor: 'secondary.main',
                },
              }}
              onClick={handleBack}
            >
              Back
            </Button>
          )}
          <Button
            variant="contained"
            color="error"
            fullWidth
            disabled={page === 3 && !verificationCode}
            sx={{
              borderRadius: '20px',
              backgroundColor: '#1F1463',
              '&:hover': { backgroundColor: 'secondary.main' },
            }}
            onClick={handleNext}
          >
            {page === 2 ? 'Sign Up' : page === 3 ? 'Verify & Complete' : 'Next'}
          </Button>
        </Box>
      </Box>
    </Box>
  );
};

export default NewUser;