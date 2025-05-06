import React from 'react';
import { Box, Typography, Divider } from '@mui/material';
import { useUser } from '../utilities/UserContext';
import AppHeader from '../components/AppHeader';
import { useLocation, useNavigate } from 'react-router-dom';

const UserProfile = () => {
  const { userData } = useUser();
  const location = useLocation();
  const navigate = useNavigate();

  const isAdmin = location.pathname.startsWith('/admin');

  const renderField = (label, value) => (
    <Box mb={2}>
      <Typography variant="body2" color="textSecondary">{label}:</Typography>
      <Typography variant="body1">
        {value || (
          <span style={{ color: '#1F1463', cursor: 'pointer' }}>+ Add {label}</span>
        )}
      </Typography>
    </Box>
  );

  const handleBack = () => navigate(-1);

  return (
    <Box bgcolor="white" minHeight="100vh">
      {/* Sticky Header */}
      <AppHeader username={userData.username || "Admin"} showSwitch={true} style={{ position: 'sticky', top: 0, zIndex: 999 }} />

      {/* Back to Chat */}
      <Box display="flex" justifyContent="center" alignItems="center" mt={4} px={2}>
        <Typography
          variant="body2"
          sx={{ color: '#1F1463', cursor: 'pointer' }}
          onClick={handleBack}
        >
          &lt; Back to chat
        </Typography>
      </Box>

      {/* Centered Profile Box */}
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
            <Typography variant="h5" fontWeight="bold" color={"#1F1463"}>
              {isAdmin ? "Admin Profile" : "User Profile"}
            </Typography>
          </Box>

          {/* Conditionally render profile fields */}
          <Box display="grid" gridTemplateColumns="1fr 1fr" gap={2}>
            {isAdmin ? (
              <>
                {renderField("Name", "Admin")}
                {renderField("Email", "admin@gmail.com")}
              </>
            ) : (
              <>
                {renderField('First Name', userData.givenName)}
                {renderField('Last Name', userData.lastName)}
                {renderField('Username', userData.username)}
                {renderField('Email', userData.email)}
                {renderField('ZipCode', userData.zipcode)}
                {renderField('Phone Number', userData.phoneNumber)}
              </>
            )}
          </Box>

          {/* Child Profile (only for regular users) */}
          {!isAdmin && (
            <>
              <Divider sx={{ my: 4 }} />
              <Box display="flex" justifyContent="space-between" alignItems="center" mb={2}>
                <Typography variant="h5" fontWeight="bold" color={"#1F1463"}>
                  Child Profile
                </Typography>
                <Typography variant="body2" sx={{ color: '#1F1463', cursor: 'pointer' }}>
                  Edit Child
                </Typography>
              </Box>

              <Box display="flex" flexDirection="column" gap={1}>
                <Typography variant="body2" sx={{ color: '#1F1463', cursor: 'pointer' }}>
                  + Add new Child Info
                </Typography>
                <Typography variant="body2" sx={{ color: '#1F1463', cursor: 'pointer' }}>
                  + Add Expected Due Date
                </Typography>
              </Box>
            </>
          )}
        </Box>
      </Box>
    </Box>
  );
};

export default UserProfile;
