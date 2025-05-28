import React, { useState, useEffect } from 'react';
import { Box, Tabs, Tab, Divider } from '@mui/material';
import { useNavigate } from 'react-router-dom';
import AppHeader from '../Components/AppHeader';
import { useUser } from "../utilities/UserContext";
import DashboardTab from '../Components/DashboardTab';
import ReferralDatabaseTab from '../Components/ReferralDatabaseTab';
import { getCurrentUser } from 'aws-amplify/auth';

const AdminDashboard = () => {
  const [activeTab, setActiveTab] = useState(0);
  const { userData, updateUser, fetchUserWithFeedback, isLoading } = useUser();
  const [isInitializing, setIsInitializing] = useState(true);
  const navigate = useNavigate();

  // Initialize user data on component mount or page reload
  useEffect(() => {
    const initializeUserData = async () => {
      try {
        // Check if we already have user data
        if (userData.username && userData.user_id) {
          setIsInitializing(false);
          return;
        }

        // Try to get current authenticated user from Amplify
        const currentUser = await getCurrentUser();

        if (currentUser?.username) {
          // Fetch complete user data including feedback questions
          try {
            await fetchUserWithFeedback(currentUser.username, 'english');
          } catch (fetchError) {
            console.error("Error fetching user data:", fetchError);
            // If fetch fails, at least set the username from Amplify
            updateUser({
              username: currentUser.username,
              user_id: currentUser.username
            });
          }
        } else {
          // No authenticated user found, redirect to login
          console.log("No authenticated user found, redirecting to login");
          navigate('/');
          return;
        }
      } catch (error) {
        console.error("Error getting current user:", error);
        // Redirect to login if user is not authenticated
        navigate('/');
        return;
      } finally {
        setIsInitializing(false);
      }
    };

    initializeUserData();
  }, [userData.username, userData.user_id, fetchUserWithFeedback, updateUser, navigate]);

  const handleTabChange = (event, newValue) => {
    setActiveTab(newValue);
  };

  // Show loading state while initializing
  if (isInitializing || isLoading) {
    return (
      <Box
        sx={{
          height: '100vh',
          display: 'flex',
          justifyContent: 'center',
          alignItems: 'center'
        }}
      >
        <div>Loading...</div>
      </Box>
    );
  }

  return (
    <>
      <AppHeader
        username={userData?.username || userData?.user_id || "User"}
        showSwitch={true}
        style={{ position: 'sticky', top: 0, zIndex: 999 }}
      />

      <Box sx={{ mt: '64px', height: 'calc(100vh - 64px)', display: 'flex', flexDirection: 'column' }}>
        <Box sx={{ bgcolor: 'background.paper', px: 4 }}>
          <Tabs
            value={activeTab}
            onChange={handleTabChange}
            indicatorColor="primary"
            textColor="primary"
            aria-label="admin tabs"
            sx={{ alignSelf: 'flex-start' }}
          >
            <Tab label="Dashboard" />
            <Tab label="Referral Database" />
          </Tabs>
        </Box>
        <Divider />

        <Box sx={{ flexGrow: 1, p: 4, overflowY: 'auto' }}>
          {activeTab === 0 && <DashboardTab />}
          {activeTab === 1 && <ReferralDatabaseTab />}
        </Box>
      </Box>
    </>
  );
};

export default AdminDashboard;