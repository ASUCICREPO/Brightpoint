import React, { useState } from "react";
import { Grid, AppBar, Menu, MenuItem, Typography, IconButton } from "@mui/material";
import Logo from "../Assets/Brightpoint_logo.svg";
import accountIcon from "../Assets/account_icon.svg";
import dropdownIcon from "../Assets/dropdown.svg"; // Importing dropdown icon
import { useNavigate } from "react-router-dom"; // Import useNavigate

function AppHeader({ username }) {
  const [anchorEl, setAnchorEl] = useState(null);
  const navigate = useNavigate(); // Initialize useNavigate

  const handleMenuOpen = (event) => {
    setAnchorEl(event.currentTarget);
  };

  const handleMenuClose = () => {
    setAnchorEl(null);
  };

  const handleLogout = () => {
    // Logic for logging out the user (if applicable)
    // e.g., clearing tokens, session, etc.

    // Redirect to home page after logout
    navigate("/"); // This will navigate the user to the '/' route
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
        sx={{ padding: "0 3rem" }}
        className="appHeight100"
      >
        {/* Logo */}
        <Grid item>
          <img src={Logo} alt="App main Logo" height={44} />
        </Grid>

        {/* Profile Dropdown */}
        <Grid item>
          <IconButton
            onClick={handleMenuOpen}
            sx={{
              display: "flex",
              alignItems: "center",
              gap: 1,
              "&:hover": { backgroundColor: "transparent" }, // Prevent oval hover effect
            }}
          >
            <img src={accountIcon} alt="Profile Icon" height={32} />
            <Typography variant="subtitle1" sx={{ fontWeight: "bold", color: "#1F1463" }}>
              {username}
            </Typography>
            <img src={dropdownIcon} alt="Dropdown Icon" height={12} />
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
                  "&:hover": { backgroundColor: "transparent" }, // Remove hover background
                },
              },
            }}
          >
            <MenuItem onClick={handleMenuClose}>View Profile</MenuItem>
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
