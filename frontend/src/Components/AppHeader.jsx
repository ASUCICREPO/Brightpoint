import React, { useState } from "react";
import {
  Grid,
  AppBar,
  Menu,
  MenuItem,
  Typography,
  IconButton,
  useMediaQuery,
  useTheme,
} from "@mui/material";
import Logo from "../Assets/Brightpoint_logo.svg";
import accountIcon from "../Assets/account_icon.svg";
import dropdownIcon from "../Assets/dropdown.svg";
import { useNavigate, useLocation } from "react-router-dom";
import ChevronLeftIcon from "@mui/icons-material/ChevronLeft";
import ChevronRightIcon from "@mui/icons-material/ChevronRight";
import { useUser } from "../utilities/UserContext"; // Import UserContext

function AppHeader({ username, isCollapsed, onNavToggle }) {
  const [anchorEl, setAnchorEl] = useState(null);
  const [isLoggingOut, setIsLoggingOut] = useState(false);
  const navigate = useNavigate();
  const location = useLocation();
  const theme = useTheme();
  const isSmallScreen = useMediaQuery(theme.breakpoints.down("sm"));
  const { logout } = useUser(); // Get logout function from context

  const handleMenuOpen = (event) => {
    setAnchorEl(event.currentTarget);
  };

  const handleMenuClose = () => {
    setAnchorEl(null);
  };

  const handleProfile = () => {
    navigate("/userprofile");
    handleMenuClose();
  };

  const handleLogout = async () => {
    if (isLoggingOut) return; // Prevent multiple logout attempts

    setIsLoggingOut(true);
    handleMenuClose();

    try {
      console.log("Starting logout process...");

      // Call the proper logout function from UserContext
      const success = await logout();

      if (success) {
        console.log("Logout successful, redirecting to login...");

        // Navigate to login page
        navigate('/', { replace: true });

        // Force a complete page reload to ensure clean state
        setTimeout(() => {
          window.location.href = '/';
        }, 100);
      }
    } catch (error) {
      console.error("Logout failed:", error);

      // Even if logout fails, force redirect to login
      navigate('/', { replace: true });
      setTimeout(() => {
        window.location.href = '/';
      }, 100);
    } finally {
      setIsLoggingOut(false);
    }
  };

  // Check if current path starts with /admin
  const isAdminRoute = location.pathname.startsWith("/admin");

  return (
    <AppBar
      position="static"
      sx={{
        backgroundColor: "#F5F8FE",
        height: "5rem",
        boxShadow: "none",
        borderBottom: (theme) => `1.5px solid ${theme.palette.primary[50]}`,
      }}
    >
      <Grid
        container
        direction="row"
        justifyContent="space-between"
        alignItems="center"
        sx={{
          padding: isSmallScreen ? "0 1rem" : "0 3rem",
          height: "100%",
          flexWrap: "nowrap",
        }}
      >
        {/* Logo */}
        <Grid item>
          <img
            src={Logo}
            alt="App main Logo"
            height={40}
            style={{ maxWidth: "100%" }}
          />
        </Grid>

        {/* Profile Dropdown */}
        <Grid item>
          <IconButton
            onClick={handleMenuOpen}
            disabled={isLoggingOut}
            sx={{
              display: "flex",
              alignItems: "center",
              gap: 1,
              "&:hover": { backgroundColor: "transparent" },
              padding: isSmallScreen ? "4px" : "8px",
              opacity: isLoggingOut ? 0.6 : 1,
            }}
          >
            <img src={accountIcon} alt="Profile Icon" height={28} />
            {!isSmallScreen && (
              <Typography
                variant="subtitle1"
                sx={{ fontWeight: "bold", color: "#1F1463", whiteSpace: "nowrap" }}
              >
                {username}
              </Typography>
            )}
            <img src={dropdownIcon} alt="Dropdown Icon" height={10} />
          </IconButton>

          <Menu
            anchorEl={anchorEl}
            open={Boolean(anchorEl) && !isLoggingOut}
            onClose={handleMenuClose}
            PaperProps={{
              elevation: 0,
              sx: {
                mt: 1.5,
                boxShadow: "0px 4px 12px rgba(0, 0, 0, 0.1)",
                minWidth: 150,
                "& .MuiMenuItem-root": {
                  "&:hover": { backgroundColor: "rgba(0, 0, 0, 0.04)" },
                },
              },
            }}
          >
            {/* Conditionally render View Profile only if NOT on /admin path */}
            {!isAdminRoute && (
              <MenuItem onClick={handleProfile}>
                View Profile
              </MenuItem>
            )}
            <MenuItem
              onClick={handleLogout}
              disabled={isLoggingOut}
              sx={{
                color: isLoggingOut ? "gray" : "red",
                opacity: isLoggingOut ? 0.6 : 1
              }}
            >
              {isLoggingOut ? "Logging out..." : "Logout"}
            </MenuItem>
          </Menu>
        </Grid>
      </Grid>
    </AppBar>
  );
}

export default AppHeader;