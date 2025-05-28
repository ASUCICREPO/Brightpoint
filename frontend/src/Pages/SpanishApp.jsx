import React, { useState, useEffect } from "react";
import Grid from "@mui/material/Grid";
import IconButton from "@mui/material/IconButton";
import MenuIcon from "@mui/icons-material/Menu";
import useMediaQuery from "@mui/material/useMediaQuery";
import { useTheme, Drawer } from "@mui/material";
import { useNavigate } from "react-router-dom";
import AppHeader from "../Components/AppHeader";
import LeftNav from "../Components/LeftNav";
import ChatHeader from "../Components/ChatHeader";
import ChatBody from "../Components/ChatBody";
import LanguageDropdown from "../Components/LanguageDropDown";
import ModalComponent from "../Components/ModalComponent";
import { useUser } from "../utilities/UserContext";
import { getCurrentUser } from 'aws-amplify/auth';

const SpanishApp = () => {
  const { userData, updateUser, fetchUserWithFeedback, isLoading } = useUser();
  const theme = useTheme();
  const isMobile = useMediaQuery(theme.breakpoints.down("sm"));
  const navigate = useNavigate();

  const [showLeftNav, setLeftNav] = useState(false);
  const [openModal, setOpenModal] = useState(false);
  const [referralQuestions, setReferralQuestions] = useState([]);
  const [isInitializing, setIsInitializing] = useState(true);

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
            await fetchUserWithFeedback(currentUser.username, 'spanish');
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

  // Process referrals for modal
  useEffect(() => {
    const referrals = userData?.referrals || [];
    const maxAttempts = 3;

    const processReferrals = async () => {
      const processed = [];

      for (const referral of referrals) {
        let attempts = 0;
        let updatedReferral = referral;

        while (attempts < maxAttempts && updatedReferral.status !== "completed") {
          await new Promise((res) => setTimeout(res, 1000));
          attempts++;

          // Simulate no change for now
          updatedReferral = { ...updatedReferral };
        }

        if (updatedReferral.status === "completed") {
          processed.push(updatedReferral);
        } else {
          processed.push({
            ...updatedReferral,
            message: "There was some issue processing your request please try again",
          });
        }
      }

      if (processed.length > 0) {
        setReferralQuestions(processed.slice(0, 5));
        setOpenModal(true);
      }
    };

    if (referrals.length > 0 && !isInitializing) {
      processReferrals();
    }
  }, [userData, isInitializing]);

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
      {/* App Header */}
      <Grid item sx={{ position: "fixed", top: 0, left: 0, right: 0, zIndex: 10 }}>
        <AppHeader
          username={userData?.username || userData?.user_id || "User"}
          showSwitch={true}
          leftNavToggle={
            isMobile && (
              <IconButton onClick={() => setLeftNav(true)} sx={{ color: "white" }}>
                <MenuIcon />
              </IconButton>
            )
          }
        />
      </Grid>

      {/* Layout body */}
      <Grid item container direction="row" sx={{ marginTop: "80px", height: "100vh" }}>
        {/* Sidebar for Desktop */}
        {!isMobile && (
          <Grid
            item
            sx={{
              position: "fixed",
              top: "80px",
              left: 0,
              bottom: 0,
              width: "30%",
              backgroundColor: (theme) => theme.palette.background.chatLeftPanel,
              zIndex: 5,
            }}
          >
            <LeftNav showLeftNav={true} language="ES" />
          </Grid>
        )}

        {/* Drawer (Sidebar for Mobile) */}
        {isMobile && (
          <Drawer
            anchor="left"
            open={showLeftNav}
            onClose={() => setLeftNav(false)}
            PaperProps={{ sx: { width: "100%" } }}
          >
            <LeftNav showLeftNav={true} setLeftNav={setLeftNav} language="ES" />
          </Drawer>
        )}

        {/* Chat Header */}
        <Grid
          item
          container
          direction="row"
          sx={{
            position: "fixed",
            top: "80px",
            left: isMobile ? 0 : "30%",
            right: 0,
            zIndex: 5,
            backgroundColor: (theme) => theme.palette.background.paper,
            padding: "30px 0 0 10px",
            justifyContent: "center",
          }}
        >
          <Grid container alignItems="center">
            <Grid item xs={8} container justifyContent="center" paddingLeft={10}>
              <ChatHeader />
            </Grid>
            <Grid item xs={4} container justifyContent="flex-end" paddingLeft={10}>
              <LanguageDropdown />
            </Grid>
          </Grid>
        </Grid>

        {/* Chat Body */}
        <Grid
          item
          container
          sx={{
            marginTop: "200px",
            marginLeft: isMobile ? "0" : "30%",
            width: isMobile ? "100%" : "70%",
            justifyContent: "center",
            paddingX: "70px",
            paddingBottom: "30px",
          }}
        >
          <ChatBody language="spanish" />
        </Grid>
      </Grid>

      {/* Modal */}
      <ModalComponent
        openModal={openModal}
        setOpenModal={setOpenModal}
        referralQuestions={referralQuestions}
      />
    </Grid>
  );
};

export default SpanishApp;