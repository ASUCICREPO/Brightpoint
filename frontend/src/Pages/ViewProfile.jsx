import React from 'react';
import { Box, Typography, Divider } from '@mui/material';
import { useLocation, useNavigate } from 'react-router-dom';
import AppHeader from '../Components/AppHeader';
import { useUser } from '../utilities/UserContext';

const UserProfile = () => {
  const location = useLocation();
  const navigate = useNavigate();
  const isAdmin = location.pathname.startsWith('/admin');

  const { userData } = useUser();

  // ✅ Helper function to get the username display value (username or user_id)
  const getDisplayUsername = () => {
    const username = userData?.username?.toString().trim();
    const user_id = userData?.user_id?.toString().trim();

    // Return username if it exists and is not empty, otherwise return user_id
    return username || user_id || "-";
  };

  // ✅ Helper function to get phone number with all possible field variations
  const getPhoneNumber = () => {
    // Try all possible phone number field names
    const phoneFields = [
      userData?.phoneNumber,      // camelCase (most common in React)
      userData?.Phone,           // API format (capital P)
      userData?.phone,           // lowercase
      userData?.phonenumber,     // form field name
      userData?.phoneNum,        // another variation
      userData?.mobile,          // alternative field name
    ];

    // Return the first non-empty value
    const phoneNumber = phoneFields.find(field =>
      field && field.toString().trim() !== ''
    );

    return phoneNumber?.toString().trim() || "-";
  };

  // ✅ Helper function to get zipcode with variations
  const getZipcode = () => {
    return userData?.zipcode ||
           userData?.Zipcode ||
           userData?.zip ||
           userData?.postalCode ||
           "-";
  };

  const renderField = (label, value) => (
    <Box mb={2}>
      <Typography variant="body2" color="textSecondary">{label}:</Typography>
      <Typography variant="body1">
        {value?.toString().trim() ? value : "-"}
      </Typography>
    </Box>
  );

  const handleBack = () => {
    console.log("Navigating back");
    navigate(-1);
  };

  // ✅ Comprehensive debug logging
  console.log('🔍 UserProfile userData debug:', {
    userData,
    availableKeys: Object.keys(userData || {}),
    phoneFields: {
      phoneNumber: userData?.phoneNumber,
      Phone: userData?.Phone,
      phone: userData?.phone,
      phonenumber: userData?.phonenumber,
    },
    userIdFields: {
      username: userData?.username,
      user_id: userData?.user_id,
    },
    chosenValues: {
      displayUsername: getDisplayUsername(),
      phoneNumber: getPhoneNumber(),
      zipcode: getZipcode(),
    }
  });

  return (
    <Box bgcolor="white" minHeight="100vh">
      <AppHeader
        username={getDisplayUsername()}
        showSwitch={true}
        style={{ position: 'sticky', top: 0, zIndex: 999 }}
      />

      <Box display="flex" justifyContent="center" alignItems="center" mt={4} px={2}>
        <Typography
          variant="body2"
          sx={{ color: '#1F1463', cursor: 'pointer' }}
          onClick={handleBack}
        >
          &lt; Back to chat
        </Typography>
      </Box>

      <Box display="flex" justifyContent="center" alignItems="center" mt={4} px={2}>
        <Box
          width="100%"
          maxWidth="600px"
          bgcolor="white"
          p={4}
          borderRadius={4}
          boxShadow={3}
        >
          <Box display="flex" justifyContent="space-between" alignItems="center" mb={3}>
            <Typography variant="h5" fontWeight="bold" color="#1F1463">
              {isAdmin ? "Admin Profile" : "User Profile"}
            </Typography>
          </Box>

          <Box display="grid" gridTemplateColumns="1fr 1fr" gap={2}>
            {isAdmin ? (
              <>
                {renderField("Name", "Admin")}
                {renderField("Email", "admin@gmail.com")}
              </>
            ) : (
              <>
                {renderField("Username", getDisplayUsername())}
                {renderField("Email", userData?.email)}
                {renderField("ZipCode", getZipcode())}
                {renderField("Phone Number", getPhoneNumber())}
              </>
            )}
          </Box>

          {!isAdmin && (
            <>
              <Divider sx={{ my: 4 }} />
              <Box display="flex" justifyContent="space-between" alignItems="center" mb={2}>
                <Typography variant="h5" fontWeight="bold" color="#1F1463">
                  Child Profile
                </Typography>
                <Typography variant="body2" sx={{ color: '#1F1463', cursor: 'pointer' }}>
                  Edit Child
                </Typography>
              </Box>

              <Box display="flex" flexDirection="column" gap={1}>
                {renderField("Child Info", userData?.childInfo)}
                {renderField("Expected Due Date", userData?.dueDate)}
              </Box>
            </>
          )}
        </Box>
      </Box>
    </Box>
  );
};

export default UserProfile;