import React, { useState, useEffect } from "react";
import Grid from "@mui/material/Grid";
import AppHeader from "../Components/AppHeader";
import LeftNav from "../Components/LeftNav";
import ChatHeader from "../Components/ChatHeader";
import ChatBody from "../Components/ChatBody";
import LanguageDropdown from "../Components/LanguageDropDown";
import ModalComponent from "../Components/ModalComponent";
import { useUser } from "../utilities/UserContext";

const MainApp = () => {
  const { userData } = useUser(); // Assume userData.referrals is available
  const [showLeftNav, setLeftNav] = useState(true);
  const [openModal, setOpenModal] = useState(false);
  const [referralQuestions, setReferralQuestions] = useState([]);

  useEffect(() => {
    // Check if referrals exist and update modal state
    const referrals = userData?.referrals || []; // Assuming this array exists in context
    if (referrals.length > 0) {
      setReferralQuestions(referrals.slice(0, 5)); // First 5 only
      setOpenModal(true);
    }
  }, [userData]);

  return (
    <Grid container direction="column" className="appHeight100">
      <Grid item sx={{ position: "fixed", top: 0, left: 0, right: 0, zIndex: 10 }}>
        <AppHeader username={userData?.username || "johndoe"} showSwitch={true} />
      </Grid>

      <Grid item container direction="row" sx={{ marginTop: "80px", height: "100vh" }}>
        <Grid item sx={{ position: "fixed", top: "80px", left: 0, bottom: 0, width: "30%", backgroundColor: (theme) => theme.palette.background.chatLeftPanel, zIndex: 5 }}>
          <LeftNav showLeftNav={showLeftNav} setLeftNav={setLeftNav} />
        </Grid>

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

      {/* Modal only opens if referrals exist */}
      <ModalComponent
        openModal={openModal}
        setOpenModal={setOpenModal}
        referralQuestions={referralQuestions}
      />
    </Grid>
  );
};

export default MainApp;
