import React, { useState } from 'react';
import { Box, Tabs, Tab, Divider } from '@mui/material';
import AppHeader from '../Components/AppHeader';
import { useUser } from "../utilities/UserContext";
import DashboardTab from '../Components/DashboardTab';
import ReferralDatabaseTab from '../Components/ReferralDatabaseTab';

const AdminDashboard = () => {
  const [activeTab, setActiveTab] = useState(0);
  const { userData } = useUser();

  const handleTabChange = (event, newValue) => {
    setActiveTab(newValue);
  };

  return (
    <>
      <AppHeader
        username={userData.username || "johndoe"}
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
