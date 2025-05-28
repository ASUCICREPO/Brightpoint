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
import { Amplify } from 'aws-amplify';
import awsExports from './aws-exports';
import AdminLanding from './Pages/AdminLanding';
import AdminDashboard from './Pages/AdminDashboard';
import UserProfilePage from "./Pages/ViewProfile";
import SpanishApp from "./Pages/SpanishApp";
import PolishApp from "./Pages/PolishApp";
import AuthProvider from "./utilities/AuthProvider";
import ProtectedRoute from "./utilities/ProtectedRoute";
import AdminRoute from "./utilities/AdminRoute";

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
            <AuthProvider>
            <Router>
              <Routes>
                <Route path="/" element={<LandingPage setOpenModal={setOpenModal} />} />
                <Route path="/newsignup" element={<NewSignUp />} />
                <Route path="/newusersignup" element={ <ProtectedRoute><NewUser /></ProtectedRoute>} />
                <Route path="/app" element={<ProtectedRoute><MainApp /></ProtectedRoute>} />
                <Route path="/esapp" element={<ProtectedRoute><SpanishApp /></ProtectedRoute>} />
                <Route path="/plapp" element={<ProtectedRoute><PolishApp /></ProtectedRoute>} />
                <Route path="/userprofile" element={<ProtectedRoute><UserProfilePage /></ProtectedRoute>} />
                <Route path="/admin" element={<AdminLanding />} />
                <Route path="/admindashboard" element={<AdminRoute><AdminDashboard /></AdminRoute>} />
              </Routes>
            </Router>
            </AuthProvider>
          </ThemeProvider>
        </TranscriptProvider>
      </LanguageProvider>
    </UserProvider>
  );
}

export default App;
