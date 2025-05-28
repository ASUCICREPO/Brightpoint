import React, { useState } from "react";
import theme from "./theme";
import { ThemeProvider } from "@mui/material/styles";
import { LanguageProvider } from "./utilities/LanguageContext";
import { UserProvider } from "./utilities/UserContext";
import LandingPage from "./Pages/LandingPage";
import { useCookies } from "react-cookie";
import { TranscriptProvider } from './utilities/TranscriptContext';
import { BrowserRouter as Router, Routes, Route, useLocation } from "react-router-dom";
import NewSignUp from "./Pages/NewSignUp";
import NewUser from "./Pages/NewUser";
import MainApp from "./Pages/MainApp";
import ReferralApp from "./Pages/ReferralApp";
import { Amplify } from 'aws-amplify';
import awsExports from './aws-exports';
import AdminLanding from './Pages/AdminLanding';
import AdminDashboard from './Pages/AdminDashboard';
import UserProfilePage from "./Pages/ViewProfile";
import { Dashboard } from "@mui/icons-material";
import DashboardTab from "./Components/DashboardTab";
import ReferralDatabase from "./Components/ReferralDatabaseTab";
import SpanishApp from "./Pages/SpanishApp";
import PolishApp from "./Pages/PolishApp";
Amplify.configure(awsExports);

function App() {
  const [cookies] = useCookies(['language']);
  const languageSet = Boolean(cookies.language);
  const [openModal, setOpenModal] = useState(false);
  // const location = useLocation();
  // const appName = location.pathname.startsWith("/admin") ? "BrightPoint Admin Portall" : "BrightPoint Referral Agent";


  return (
    <UserProvider>
      <LanguageProvider>
        <TranscriptProvider>
          <ThemeProvider theme={theme}>
            <Router>
              <Routes>
                <Route path="/" element={<LandingPage setOpenModal={setOpenModal} />} />
                <Route path="/app" element={<MainApp />} />
                <Route path="/esapp" element={<SpanishApp />} />
                <Route path="/plapp" element={<PolishApp />} />
                <Route path="/newsignup" element={<NewSignUp />} />
                <Route path="/newusersignup" element={<NewUser />} />
                <Route path="/referralapp" element={<ReferralApp />} />
                <Route path="/userprofile" element={<UserProfilePage />} />
                <Route path="/admin" element={<AdminLanding />} />
                <Route path="/admindashboard" element={<AdminDashboard />} />
                <Route path="/analytics" element={<DashboardTab />} />
                <Route path="/referral" element={<ReferralDatabase />} />

              </Routes>
            </Router>
          </ThemeProvider>
        </TranscriptProvider>
      </LanguageProvider>
    </UserProvider>
  );
}

export default App;
