import React, { useState, useEffect } from "react";
import Grid from "@mui/material/Grid";
import IconButton from "@mui/material/IconButton";
import MenuIcon from "@mui/icons-material/Menu";
import useMediaQuery from "@mui/material/useMediaQuery";
import { useTheme, Drawer } from "@mui/material";
import AppHeader from "../Components/AppHeader";
import LeftNav from "../Components/LeftNav";
import ChatHeader from "../Components/ChatHeader";
import ChatBody from "../Components/ChatBody";
import LanguageDropdown from "../Components/LanguageDropDown";
import ModalComponent from "../Components/ModalComponent";
import { useUser } from "../utilities/UserContext";

const MainApp = () => {
  const { userData } = useUser();
  const theme = useTheme();
  const isMobile = useMediaQuery(theme.breakpoints.down("sm"));

  const [showLeftNav, setLeftNav] = useState(false);
  const [openModal, setOpenModal] = useState(false);
  const [referralQuestions, setReferralQuestions] = useState([]);

  // ✅ REMOVED: Auto-opening logic (let ModalComponent handle this with proper session tracking)
  // ✅ OPTIONAL: Keep this effect only for debugging/logging
  useEffect(() => {
    const feedbackQuestions = userData?.feedbackQuestions || [];

  }, [userData, openModal]);

  return (
    <Grid container direction="column" className="appHeight100">
      {/* App Header */}
      <Grid item sx={{ position: "fixed", top: 0, left: 0, right: 0, zIndex: 10 }}>
        <AppHeader
          username={userData?.username || userData?.user_id || "johndoe"}
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
            <LeftNav showLeftNav={true} language="EN" />
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
            <LeftNav showLeftNav={true} setLeftNav={setLeftNav} language="EN" />
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
          <ChatBody language={"english"} />
        </Grid>
      </Grid>

      {/* ✅ Modal - Now fully controlled by ModalComponent's internal logic */}
      <ModalComponent
        openModal={openModal}
        setOpenModal={setOpenModal}
      />
    </Grid>
  );
};

export default MainApp;