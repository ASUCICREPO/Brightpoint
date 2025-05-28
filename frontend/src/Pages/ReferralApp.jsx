import React, { useState, useEffect } from "react";
import Grid from "@mui/material/Grid";
import { useNavigate } from "react-router-dom";
import AppHeader from "../Components/AppHeader";
import LeftNav from "../Components/LeftNav";
import ChatHeader from "../Components/ChatHeader";
import ChatBody from "../Components/ChatBody";
import LanguageDropdown from "../Components/LanguageDropDown";
import { useLocation } from "react-router-dom";
import { useUser } from "../utilities/UserContext";
import { getCurrentUser } from 'aws-amplify/auth';

const ReferralApp = () => {
  const { userData, updateUser, fetchUserWithFeedback, isLoading } = useUser();
  const [showLeftNav, setLeftNav] = useState(true);
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

  // Show loading state while initializing
  if (isInitializing || isLoading) {
    return (
      <Grid container direction="column" className="appHeight100" justifyContent="center" alignItems="center">
        <div>Loading...</div>
      </Grid>
    );
  }

  return (
    <Grid container direction="column" className="appHeight100">
      {/* App Header - Fixed at the top */}
      <Grid item sx={{ position: "fixed", top: 0, left: 0, right: 0, zIndex: 10 }}>
        <AppHeader username={userData?.username || userData?.user_id || "User"} showSwitch={true} />
      </Grid>

      {/* Main content area */}
      <Grid item container direction="row" sx={{ marginTop: "80px", height: "100vh" }}>
        {/* Left Nav - Fixed on the left side, takes up 30% of width */}
        <Grid item sx={{ position: "fixed", top: "80px", left: 0, bottom: 0, width: "30%", backgroundColor: (theme) => theme.palette.background.chatLeftPanel, zIndex: 5 }}>
          <LeftNav showLeftNav={showLeftNav} setLeftNav={setLeftNav} />
        </Grid>

        {/* Chat Header & Language Dropdown - Fixed on top of content, next to Left Nav, taking up 70% */}
        <Grid
          item
          container
          direction="row"
          sx={{
            position: "fixed",
            top: "80px",
            left: "30%",
            right: 0,
            zIndex: 5,
            backgroundColor: (theme) => theme.palette.background.paper,
            padding: "30px",
            justifyContent: "center", // Center align the content horizontally
            paddingLeft: "10px", // Add padding on the left side
            paddingRight: "0px", // Add padding on the right side
          }}
        >
          <Grid container alignItems="center">
            {/* Empty Column */}
            <Grid item xs={2} />

            {/* Centered Chat Header */}
            <Grid item xs={10} container justifyContent="center" paddingLeft={30}>
              <ChatHeader />
            </Grid>

            {/* Right-Aligned Language Dropdown */}
            <Grid item xs={4} container justifyContent="flex-end" paddingLeft={20}>
              <LanguageDropdown />
            </Grid>
          </Grid>
        </Grid>

        {/* Chat Body - Takes up the remaining 70%, below the chat header */}
        <Grid
          item
          container
          sx={{
            marginTop: "200px", // Adjust this margin to accommodate the header and dropdown
            marginLeft: "30%", // The left margin to align with the left nav
            width: "80%", // The width to occupy the rest of the space
            justifyContent: "center", // Center align the content horizontally
            paddingLeft: "70px", // Add padding on both sides of the Chat Body
            paddingRight: "70px",
            paddingBottom: "30px"
          }}
        >
          <ChatBody />
        </Grid>
      </Grid>
    </Grid>
  );
};

export default ReferralApp;