import React, { useState, useEffect} from "react";
import Grid from "@mui/material/Grid";
import AppHeader from "../Components/AppHeader";
import LeftNav from "../Components/LeftNav";
import ChatHeader from "../Components/ChatHeader";
import ChatBody from "../Components/ChatBody";
import LanguageDropdown from "../Components/LanguageDropDown";
import { useLocation } from "react-router-dom";
import { useUser } from "../utilities/UserContext"; // Import user context

const  MainApp= () => {
  const { userData } = useUser(); // Get username & zipCode from context
  const [showLeftNav, setLeftNav] = useState(true);
  
    return (
      <Grid container direction="column" className="appHeight100">
        {/* App Header - Fixed at the top */}
        <Grid item sx={{ position: "fixed", top: 0, left: 0, right: 0, zIndex: 10 }}>
          <AppHeader username={userData.username || "johndoe"} showSwitch={true} />
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
              <Grid item xs={4} container justifyContent="flex-end"  paddingLeft={20}>
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

export default MainApp;
