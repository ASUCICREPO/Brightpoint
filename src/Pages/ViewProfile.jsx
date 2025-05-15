import React, { useEffect, useState } from 'react';
import { Box, Typography, Divider } from '@mui/material';
import { useLocation, useNavigate } from 'react-router-dom';
import AppHeader from '../components/AppHeader';
import { USER_API } from '../utilities/constants';
import { useUser } from '../utilities/UserContext'; // ✅ Import context

const UserProfile = () => {
  const location = useLocation();
  const navigate = useNavigate();
  const isAdmin = location.pathname.startsWith('/admin');

  const [localUserData, setLocalUserData] = useState({});
  const { userData, updateUser } = useUser(); // ✅ Use context
  const userId = userData.user_id // Update as needed

  useEffect(() => {
    console.log("Opening WebSocket connection to:", USER_API);
    const ws = new WebSocket(USER_API);

    ws.onopen = () => {
      const payload = { action: "getUser", user_id: userId };
      console.log("WebSocket connection opened, sending payload:", payload);
      ws.send(JSON.stringify(payload));
    };

    ws.onmessage = (event) => {
      console.log("WebSocket message received:", event.data);
      try {
        const data = JSON.parse(event.data);
        if (data && data.user) {
          console.log("Parsed user data:", data.user);
          setLocalUserData(data.user);
          updateUser(data.user); // ✅ Update global context
        } else {
          console.warn("No 'user' object found in response:", data);
        }
      } catch (err) {
        console.error("Failed to parse WebSocket message:", err);
      }
    };

    ws.onerror = (error) => {
      console.error("WebSocket error:", error);
    };

    ws.onclose = () => {
      console.log("WebSocket connection closed");
    };

    return () => {
      console.log("Closing WebSocket connection");
      ws.close();
    };
  }, []);

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

  return (
    <Box bgcolor="white" minHeight="100vh">
      <AppHeader
        username={userData.username || userData.user_id|| "Admin"}
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
                {/* {renderField("First Name", userData.firstName)}
                {renderField("Last Name", userData.lastName)} */}
                {renderField("Username", userData.user_id)}
                {renderField("Email", userData.email)}
                {renderField("ZipCode", userData.zipcode)}
                {renderField("Phone Number", userData.phoneNumber)}
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
                {renderField("Child Info", userData.childInfo)}
                {renderField("Expected Due Date", userData.dueDate)}
              </Box>
            </>
          )}
        </Box>
      </Box>
    </Box>
  );
};

export default UserProfile;
