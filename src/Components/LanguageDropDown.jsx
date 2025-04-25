import React, { useState } from "react";
import { Menu, MenuItem, Button, Box, Divider } from "@mui/material";
import { useLanguage } from "../utilities/LanguageContext"; // Adjust the path
import LanguageIcon from "../Assets/language.svg"; // Adjust the path
import DropdownIcon from "../Assets/dropdown_white.svg"; // Adjust the path

function LanguageDropdown() {
  const [anchorEl, setAnchorEl] = useState(null);
  const { language, setLanguage } = useLanguage();

  const handleClick = (event) => {
    setAnchorEl(event.currentTarget);
  };

  const handleClose = () => {
    setAnchorEl(null);
  };

  const handleLanguageChange = (newLang) => {
    setLanguage(newLang);
    handleClose();
  };

  const availableLanguages = [
    { code: "ES", label: "Spanish" },
    { code: "EN", label: "English" },
    { code: "PL", label: "Polish" },
  ].filter((lang) => lang.code !== language); // Remove the selected language

  return (
    <Box>
      <Button
        onClick={handleClick}
        sx={{
          backgroundColor: "#1F1463",
          color: "white",
          textTransform: "none",
          padding: "8px 16px",
          borderRadius: "8px",
          display: "flex",
          alignItems: "center",
          minWidth: "150px", // Ensures dropdown matches button width
          justifyContent: "space-between",
          "&:hover": {
            backgroundColor: "#1A1153",
          },
        }}
      >
        <img src={LanguageIcon} alt="Language" style={{ width: 20, height: 20, marginRight: 8 }} />
        {availableLanguages.find((lang) => lang.code === language)?.label || "English"}
        <img src={DropdownIcon} alt="Dropdown" style={{ width: 16, height: 16, marginLeft: 8 }} />
      </Button>
      <Menu
        anchorEl={anchorEl}
        open={Boolean(anchorEl)}
        onClose={handleClose}
        MenuListProps={{
          "aria-labelledby": "language-button",
        }}
        sx={{
          "& .MuiPaper-root": {
            backgroundColor: "white",
            color: "black",
            borderRadius: "8px",
            boxShadow: "0px 4px 10px rgba(0,0,0,0.1)",
            width: anchorEl ? anchorEl.clientWidth : "auto", // Match button width
          },
        }}
      >
        {availableLanguages.map((lang, index) => (
          <React.Fragment key={lang.code}>
            {index > 0 && <Divider />} {/* Add divider between options */}
            <MenuItem onClick={() => handleLanguageChange(lang.code)} sx={{ color: "black" }}>
              {lang.label}
            </MenuItem>
          </React.Fragment>
        ))}
      </Menu>
    </Box>
  );
}

export default LanguageDropdown;
