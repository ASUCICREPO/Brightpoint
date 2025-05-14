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
import { useNavigate } from "react-router-dom";
import ChevronLeftIcon from "@mui/icons-material/ChevronLeft";
import ChevronRightIcon from "@mui/icons-material/ChevronRight";

function AppHeader({ username, isCollapsed, onNavToggle }) {
  const [anchorEl, setAnchorEl] = useState(null);
  const navigate = useNavigate();
  const theme = useTheme();
  const isSmallScreen = useMediaQuery(theme.breakpoints.down("sm"));

  const handleMenuOpen = (event) => {
    setAnchorEl(event.currentTarget);
  };

  const handleMenuClose = () => {
    setAnchorEl(null);
  };

  const handleProfile = () => {
    navigate("/userprofile");
  };

  const handleLogout = () => {
    navigate("/");
  };

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
        {/* Collapse Toggle Icon */}
        {/* <Grid item>
          <IconButton onClick={onNavToggle} sx={{ padding: 0 }}>
            {isCollapsed ? (
              <ChevronRightIcon sx={{ fontSize: 30, color: "#1F1463" }} />
            ) : (
              <ChevronLeftIcon sx={{ fontSize: 30, color: "#1F1463" }} />
            )}
          </IconButton>
        </Grid> */}

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
            sx={{
              display: "flex",
              alignItems: "center",
              gap: 1,
              "&:hover": { backgroundColor: "transparent" },
              padding: isSmallScreen ? "4px" : "8px",
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
            open={Boolean(anchorEl)}
            onClose={handleMenuClose}
            PaperProps={{
              elevation: 0,
              sx: {
                mt: 1.5,
                boxShadow: "0px 4px 12px rgba(0, 0, 0, 0.1)",
                minWidth: 150,
                "& .MuiMenuItem-root": {
                  "&:hover": { backgroundColor: "transparent" },
                },
              },
            }}
          >
            <MenuItem onClick={handleProfile}>View Profile</MenuItem>
            <MenuItem onClick={handleLogout} sx={{ color: "red" }}>
              Logout
            </MenuItem>
          </Menu>
        </Grid>
      </Grid>
    </AppBar>
  );
}

export default AppHeader;
