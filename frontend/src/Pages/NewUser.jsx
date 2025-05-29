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

  // ✅ NEW: Phone number validation state
  const [phoneError, setPhoneError] = useState('');

  const navigate = useNavigate();

  // ✅ NEW: Phone number formatting and validation function
  const formatPhoneNumber = (phoneInput) => {
    if (!phoneInput) return '';

    // Remove all non-digit characters
    const digitsOnly = phoneInput.replace(/\D/g, '');

    // Handle different input formats
    let formattedPhone = '';

    if (digitsOnly.length === 10) {
      // 10 digits: assume US number, add +1
      formattedPhone = `+1${digitsOnly}`;
    } else if (digitsOnly.length === 11 && digitsOnly.startsWith('1')) {
      // 11 digits starting with 1: add +
      formattedPhone = `+${digitsOnly}`;
    } else if (digitsOnly.length === 11 && !digitsOnly.startsWith('1')) {
      // 11 digits not starting with 1: add +1
      formattedPhone = `+1${digitsOnly}`;
    } else if (digitsOnly.length === 12 && digitsOnly.startsWith('1')) {
      // 12 digits starting with 1: add +
      formattedPhone = `+${digitsOnly}`;
    } else {
      // Invalid length - return as is for now, will be caught by validation
      formattedPhone = phoneInput;
    }

    return formattedPhone;
  };

  // ✅ NEW: Phone number validation function
  const validatePhoneNumber = (phone) => {
    if (!phone) return 'Phone number is required';

    const digitsOnly = phone.replace(/\D/g, '');

    // Check if it's a valid US phone number (10 or 11 digits)
    if (digitsOnly.length === 10) {
      return ''; // Valid 10-digit number
    } else if (digitsOnly.length === 11 && digitsOnly.startsWith('1')) {
      return ''; // Valid 11-digit number starting with 1
    } else {
      return 'Please enter a valid US phone number (10 digits)';
    }
  };

  // ✅ NEW: Handle phone number change with formatting
  const handlePhoneChange = (event) => {
    const inputValue = event.target.value;

    // Allow user to type, but validate on blur
    setFormData(prev => ({
      ...prev,
      phonenumber: inputValue
    }));

    // Clear previous error when user starts typing
    if (phoneError) {
      setPhoneError('');
    }
  };

  // ✅ NEW: Handle phone number blur (when user leaves the field)
  const handlePhoneBlur = () => {
    const rawPhone = formData.phonenumber;

    if (!rawPhone) {
      setPhoneError('Phone number is required');
      return;
    }

    // Validate the phone number
    const validationError = validatePhoneNumber(rawPhone);
    if (validationError) {
      setPhoneError(validationError);
      return;
    }

    // Format the phone number
    const formattedPhone = formatPhoneNumber(rawPhone);

    // Update the form data with formatted phone
    setFormData(prev => ({
      ...prev,
      phonenumber: formattedPhone
    }));

    console.log(`📱 Phone formatted: "${rawPhone}" → "${formattedPhone}"`);
  };

  const handleCompleteSignup = async () => {
    const { username, password, email } = userData;
    const { givenName, lastName, zipcode, phonenumber } = formData;

    // ✅ NEW: Final phone validation before signup
    const phoneValidationError = validatePhoneNumber(phonenumber);
    if (phoneValidationError) {
      setPhoneError(phoneValidationError);
      setSnackbarMessage('Please fix the phone number before continuing.');
      setSnackbarOpen(true);
      setPage(1); // Go back to phone page
      return;
    }

    const targetPool = Amplify.getConfig().Auth?.Cognito?.userPoolId;

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
  };

  const handleEmailVerification = async () => {
    const { username } = userData;

    let isUserConfirmed = false;

    try {
      await confirmSignUp({
        username: username,
        confirmationCode: verificationCode
      });

      isUserConfirmed = true;

    } catch (error) {
      console.error("❌ VERIFICATION ERROR:");
      console.error("- Error message:", error.message);
      console.error("- Error name:", error.name);

      if (error.name === 'NotAuthorizedException' && error.message.includes('Current status is CONFIRMED')) {
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
        // ✅ ENHANCED: Ensure phone is properly formatted before sending
        const finalFormattedPhone = formatPhoneNumber(formData.phonenumber);

        const restPayload = {
          user_id: username,
          Zipcode: formData.zipcode,
          Phone: finalFormattedPhone, // ✅ Use properly formatted phone
          Email: userData.email,
          FirstName: formData.givenName,
          LastName: formData.lastName,
          Language: formData.language,
          // ✅ NEW: Add children birth dates (filter out null dates)
          children_birth_dates: formData.children
            .filter(child => child.birthDate !== null)
            .map(child => child.birthDate.toISOString().split('T')[0]), // Convert to YYYY-MM-DD format
          // ✅ NEW: Add expected due date
          expected_due_date: formData.dueDate ? formData.dueDate.toISOString().split('T')[0] : null,
          operation: "PUT",
        };

        console.log("✅ Sending payload with formatted phone:", {
          ...restPayload,
          Phone: finalFormattedPhone
        });

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

        // ✅ UPDATE USER CONTEXT with complete profile data including formatted phone
        const completeUserData = {
          username: username,
          user_id: username,  // ✅ Fix: Set user_id to username
          email: userData.email,
          zipcode: formData.zipcode,
          phoneNumber: finalFormattedPhone,  // ✅ Use formatted phone
          Phone: finalFormattedPhone,        // ✅ Also keep API format for compatibility
          firstName: formData.givenName,
          lastName: formData.lastName,
          language: formData.language,
          // ✅ NEW: Add children and due date to context
          children_birth_dates: restPayload.children_birth_dates,
          expected_due_date: restPayload.expected_due_date,
        };

        updateUser(completeUserData);

        setSnackbarMessage("Account verified and profile saved successfully!");
        setSnackbarOpen(true);

        // Navigate to language-specific route after successful verification and profile save
        setTimeout(() => {
          const lang = formData.language.toLowerCase();
          if (lang === 'spanish') {
            navigate('/esapp');
          } else if (lang === 'polish') {
            navigate('/plapp');
          } else {
            navigate('/app'); // default to English
          }
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
    // ✅ NEW: Validate phone on page 1 before proceeding
    if (page === 1) {
      const phoneValidationError = validatePhoneNumber(formData.phonenumber);
      if (phoneValidationError) {
        setPhoneError(phoneValidationError);
        setSnackbarMessage('Please enter a valid phone number before continuing.');
        setSnackbarOpen(true);
        return;
      }

      // Format phone number if valid
      const formattedPhone = formatPhoneNumber(formData.phonenumber);
      setFormData(prev => ({
        ...prev,
        phonenumber: formattedPhone
      }));
    }

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

    setFormData((prev) => {
      const updatedForm = { ...prev, [field]: value };
      return updatedForm;
    });

    if (field === 'zipcode') {
      updateUser({ ...userData, zipcode: value });
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

  // ✅ NEW: Remove child function
  const removeChild = (index) => {
    if (formData.children.length > 1) {
      const newChildren = formData.children.filter((_, i) => i !== index);
      setFormData({ ...formData, children: newChildren });
    }
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
                Phone Number <span style={{ color: 'red' }}>*</span>
              </Typography>
              <TextField
                placeholder="Enter your phone number (e.g., 925-204-8244)"
                variant="outlined"
                fullWidth
                value={formData.phonenumber}
                onChange={handlePhoneChange}
                onBlur={handlePhoneBlur}
                error={!!phoneError}
                helperText={phoneError || "Phone will be formatted as +1XXXXXXXXXX"}
                sx={{
                  backgroundColor: '#f0f0f0',
                  borderRadius: '8px',
                  '& .MuiOutlinedInput-root': {
                    borderRadius: '8px',
                  },
                }}
              />
              {/* ✅ NEW: Show current formatted phone */}
              {formData.phonenumber && !phoneError && (
                <Typography variant="caption" color="success.main" sx={{ mt: 0.5, display: 'block' }}>
                  ✓ Formatted: {formatPhoneNumber(formData.phonenumber)}
                </Typography>
              )}
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
                <Box display="flex" justifyContent="space-between" alignItems="center" mb={0.5}>
                  <Typography variant="body1">
                    Birth Date of Child #{index + 1}
                  </Typography>
                  {/* ✅ NEW: Add remove button for children (but keep at least one) */}
                  {formData.children.length > 1 && (
                    <Button
                      size="small"
                      color="error"
                      onClick={() => removeChild(index)}
                      sx={{ minWidth: 'auto', p: 0.5 }}
                    >
                      Remove
                    </Button>
                  )}
                </Box>
                <LocalizationProvider dateAdapter={AdapterDateFns}>
                  <Box width="100%" display="flex" flexDirection="column">
                    <DatePicker
                      value={child.birthDate}
                      onChange={(date) => handleChildChange(index, date)}
                      renderInput={(params) => (
                        <TextField
                          {...params}
                          fullWidth
                          sx={{
                            backgroundColor: '#f0f0f0',
                            borderRadius: '8px',
                            '& .MuiOutlinedInput-root': {
                              borderRadius: '8px',
                            },
                          }}
                        />
                      )}
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
                Expected Due Date (Optional)
              </Typography>
              <LocalizationProvider dateAdapter={AdapterDateFns}>
                <Box width="100%" display="flex" flexDirection="column">
                  <DatePicker
                    value={formData.dueDate}
                    onChange={(date) => setFormData({ ...formData, dueDate: date })}
                    renderInput={(params) => (
                      <TextField
                        {...params}
                        fullWidth
                        sx={{
                          backgroundColor: '#f0f0f0',
                          borderRadius: '8px',
                          '& .MuiOutlinedInput-root': {
                            borderRadius: '8px',
                          },
                        }}
                      />
                    )}
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
            disabled={(page === 3 && !verificationCode) || (page === 1 && !!phoneError)}
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