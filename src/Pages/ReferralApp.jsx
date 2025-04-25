import React, { useState, useEffect } from "react";
import Grid from "@mui/material/Grid";
import AppHeader from "../Components/AppHeader";
import LeftNav from "../Components/LeftNav";
import ChatHeader from "../Components/ChatHeader";
import ChatBody from "../Components/ChatBody";
import LanguageDropdown from "../Components/LanguageDropDown";
import ModalComponent from "../Components/ModalComponent"; // Import Modal Component
import { useUser } from "../utilities/UserContext"; // Commenting out user context import

const ReferralApp = () => {  
  const { userData } = useUser(); // Get username & zipCode from context
  const [showLeftNav, setLeftNav] = useState(true);
  const [openModal, setOpenModal] = useState(false); // Modal State

  // const { userData } = useUser(); // Commented out to remove user context usage
  // const firstReferralQuestion = userData?.referralQuestion || "No referral available."; // Commented out

  // Use a hardcoded question for testing the modal
  const hardcodedReferral = "Hi test, Did the referral East Peoria Food Pantry … in Food Assistance? Please reply with yes or no.";

  useEffect(() => {
    const timer = setTimeout(() => {
      setOpenModal(false);
    }, 1000); // 1000 ms = 1 second

    return () => clearTimeout(timer);
  }, []);

  return (
    <Grid container direction="column" className="appHeight100">
      {/* App Header - Fixed at the top */}
      <Grid item sx={{ position: "fixed", top: 0, left: 0, right: 0, zIndex: 10 }}>
        <AppHeader username={userData.username || "johndoe"} showSwitch={true} />
      </Grid>

      {/* Main content area */}
      <Grid item container direction="row" sx={{ marginTop: "80px", height: "100vh" }}>
        {/* Left Nav - Fixed on the left side */}
        <Grid item sx={{ position: "fixed", top: "80px", left: 0, bottom: 0, width: "30%", backgroundColor: (theme) => theme.palette.background.chatLeftPanel, zIndex: 5 }}>
          <LeftNav showLeftNav={showLeftNav} setLeftNav={setLeftNav} />
        </Grid>

        {/* Chat Header & Language Dropdown */}
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
            justifyContent: "center",
            paddingLeft: "10px",
            paddingRight: "0px",
          }}
        >
          <Grid container alignItems="center">
            <Grid item xs={8} container justifyContent="center" paddingLeft={30}>
              <ChatHeader />
            </Grid>
            <Grid item xs={4} container justifyContent="flex-end" paddingLeft={20}>
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
            marginLeft: "30%",
            width: "80%",
            justifyContent: "center",
            paddingLeft: "70px",
            paddingRight: "70px",
            paddingBottom: "30px"
          }}
        >
          <ChatBody />
        </Grid>
      </Grid>

      {/* Modal Component with the hardcoded referral question */}
      <ModalComponent openModal={openModal} setOpenModal={setOpenModal} />
    </Grid>
  );
};

export default ReferralApp;
