import React, { useState } from "react";
import theme from "./theme";
import { ThemeProvider } from "@mui/material/styles";
import { LanguageProvider } from "./utilities/LanguageContext";
import { UserProvider } from "./utilities/UserContext"; // Import UserContext
import LandingPage from "./Pages/LandingPage";
import { useCookies } from "react-cookie";
import { TranscriptProvider } from './utilities/TranscriptContext';
import { BrowserRouter as Router, Routes, Route } from "react-router-dom";
import NewSignUp from "./Pages/NewSignUp";
import NewUser from "./Pages/NewUser";
import MainApp from "./Pages/MainApp";
import ReferralApp from "./Pages/ReferralApp";
import { Amplify } from 'aws-amplify';
import awsExports from './aws-exports';
import VerifyEmail from "./Pages/VerifyEmail";

Amplify.configure(awsExports);


function App() {
  const [cookies] = useCookies(['language']);
  const languageSet = Boolean(cookies.language);
  const [openModal, setOpenModal] = useState(false);

  return (
    <UserProvider>
      <LanguageProvider>
        <TranscriptProvider>
          <ThemeProvider theme={theme}>
            <Router>
              <Routes>
                <Route path="/" element={<LandingPage setOpenModal={setOpenModal} />} />
                <Route path="/app" element={<MainApp />} />
                <Route path="/newsignup" element={<NewSignUp />} />
                <Route path="/newusersignup" element={<NewUser />} />
                <Route path="/referralapp" element={<ReferralApp />} />
                <Route path="/verifyemail" element={<VerifyEmail />} />
                
              </Routes>
            </Router>
          </ThemeProvider>
        </TranscriptProvider>
      </LanguageProvider>
    </UserProvider>
  );
}

export default App;
