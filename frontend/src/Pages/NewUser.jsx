import React, { useState, useEffect } from 'react';
import { Box, Button, Typography, TextField, RadioGroup, FormControlLabel, Radio, Snackbar, Alert, Divider, IconButton } from '@mui/material';
import BrightpointLogo from '../Assets/Brightpoint_logo.svg';
import { DatePicker, LocalizationProvider } from '@mui/x-date-pickers';
import AddIcon from '@mui/icons-material/Add';
import { AdapterDateFns } from '@mui/x-date-pickers/AdapterDateFns';
import { useNavigate } from 'react-router-dom';
import { useUser } from '../utilities/UserContext'; // Import useUser
import {signUp} from 'aws-amplify/auth';
import { USER_API , USER_ADD_API} from '../utilities/constants';
import { Auth } from 'aws-amplify';



const NewUser = () => {
  const { userData, updateUser } = useUser(); // Get user context
  const [page, setPage] = useState(0);
  const totalPages = 3;

  // Form Data State
  const [formData, setFormData] = useState({
    givenName: '',
    lastName: '',
    zipcode: '',
    email: '',
    phonenumber: '',
    language: '',
    children: [{ birthDate: null }],
    dueDate: null,
  });
  // Snackbar State
  const [snackbarOpen, setSnackbarOpen] = useState(true);

  const navigate = useNavigate(); // hook for navigation

  const handleCompleteSignup = async () => {
    const { username, password } = userData;
    const { givenName, lastName, email, zipcode, phonenumber } = formData;
  
    console.log("Starting Cognito signup...");
    console.log("Signup credentials:", { username, password });
    console.log("Attributes:", { email });
  
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
  
      console.log("✅ Cognito signUp response:", response);
  
      // REST API payload
      const restPayload = {
        user_id: username,
        Zipcode: zipcode,
        Phone: phone,
        Email: email,
        operation: "PUT",
      };
  
      console.log("📤 Sending payload to REST API:", restPayload);
  
      const restRes = await fetch(USER_ADD_API, {
        method: 'PUT',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(restPayload),
      });
  
      const restData = await restRes.json();
  
      if (!restRes.ok) {
        console.error("❌ REST API error:", restData);
        throw new Error("REST API call failed.");
      }
  
      console.log("✅ REST API response:", restData);
  
      // WebSocket message
    //   const wsPayload = {
    //     action: "createUser",
    //     user_id: username.toLowerCase(),
    //     Zipcode: zipcode,
    //     Phone: phonenumber,
    //     Email: email,
    //   };
    //   console.log("Sent request:", wsPayload);
  
    //   console.log("🌐 Connecting to WebSocket:", USER_API);
  
    //   const socket = new WebSocket(USER_API);
  
    //   socket.onopen = () => {
    //     console.log("✅ WebSocket connection opened.");
    //     socket.send(JSON.stringify(wsPayload));
    //     console.log("📤 Sent to WebSocket:", wsPayload);
    //   };
  
    //   socket.onmessage = (message) => {
    //     console.log("📨 WebSocket message received:", message.data);
    //   };
  
    //   socket.onerror = (error) => {
    //     console.error("❌ WebSocket error:", error);
    //   };
  
    //   socket.onclose = () => {
    //     console.log("🔌 WebSocket connection closed.");
    //   };
  
    // } catch (error) {
    //   console.error("❌ Error during signup or API calls:", error);
    // }
  };
  
  

  
  const handleNext = () => {
    if (page === totalPages - 1) {
      try {
        handleCompleteSignup(); // Trigger signup before navigating
        navigate('/app');     // Redirect after successful signup
      } catch (error) {
        console.error("Signup failed:", error);
        // Optional: Show error to user
      }
    } else {
      // Otherwise, go to the next page
      setPage(page + 1);
    }
  };
  const handleBack = () => {
    if (page > 0) setPage(page - 1);
  };

  const handleChange = (field) => (event) => {
    const value = event.target.value;
    
    // Log what is being captured from the input field
    console.log(`Updating field: ${field}, New Value: ${value}`);
  
    setFormData((prev) => {
      const updatedForm = { ...prev, [field]: value };
      console.log("Updated formData:", updatedForm); // Log the updated formData
      return updatedForm;
    });
  
    if (field === 'zipcode') {
      updateUser({ zipcode: value });
      console.log("User Context after zipCode update:", userData);

    }
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
      
      {/* Snackbar - Success Message */}
      <Snackbar 
        open={snackbarOpen} 
        autoHideDuration={3000} 
        onClose={() => setSnackbarOpen(false)} 
        anchorOrigin={{ vertical: 'top', horizontal: 'center' }}
      >
        <Alert severity="success" sx={{ backgroundColor: 'white', color: 'black', fontWeight: 'bold', boxShadow: 1 }}>
          Signed up Successfully
        </Alert>
      </Snackbar>

      {/* Logo */}
      <img src={BrightpointLogo} alt="Brightpoint Logo" height="60" style={{ marginBottom: 10 }} />

      {/* Multipage Container */}
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
        {/* Progress Indicator - Spanning full width of the container */}
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
          Welcome!
        </Typography>

        {/* Page 1: First Name, Last Name, Zip Code */}
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
                  value={formData[label.toLowerCase().replace(' ', '')]}
                  onChange={handleChange(label.toLowerCase().replace(' ', ''))}
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

        {/* Page 2: Email, Phone, Preferred Language */}
        {page === 1 && (
          <>
            {['Email', 'Phone Number'].map((label, index) => (
              <Box key={index} width="100%" mb={2}>
                <Typography variant="body1" alignSelf="flex-start" mb={0.5}>
                  {label}
                </Typography>
                <TextField
                  placeholder={`Enter your ${label.toLowerCase()}`}
                  variant="outlined"
                  fullWidth
                  value={formData[label.toLowerCase().replace(' ', '')]}
                  onChange={handleChange(label.toLowerCase().replace(' ', ''))}
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
                    control={<Radio />} // Hides default radio button
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


        {/* Page 3: Add Child Info */}
        {page === 2 && (
          <>
            <Typography variant="h5" color="#1F1463" gutterBottom fontWeight="bold">
              Add Child Info
            </Typography>

            {/* Child #1 Birth Date */}
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
                        fullWidth
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

            {/* Divider */}
            <Divider sx={{ width: '100%', marginBottom: 2 }} />

            {/* Expected Due Date */}
            <Box width="100%" mb={2}>
              <Typography variant="body1" alignSelf="flex-start" mb={0.5}>
                Expected Due Date 
              </Typography>
              <LocalizationProvider dateAdapter={AdapterDateFns} >
              <Box width="100%" display="flex" flexDirection="column">

                <DatePicker
                  value={formData.dueDate}
                  onChange={(date) => setFormData({ ...formData, dueDate: date })}
                  renderInput={(params) => <TextField {...params} fullWidth />}
                  fullWidth
                />
                </Box>
              </LocalizationProvider>
            </Box>
          </>
        )}

        {/* Navigation Buttons */}
        <Box display="flex" width="100%" mt={3} gap={2}>
          {page > 0 && (
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
            sx={{
              borderRadius: '20px',
              backgroundColor: '#1F1463',
              '&:hover': { backgroundColor: 'secondary.main' },
            }}
            onClick={handleNext}
          >
            {page === totalPages - 1 ? 'Start Chat' : 'Next'}
          </Button>
        </Box>
      </Box>
    </Box>
  );
};

export default NewUser;
