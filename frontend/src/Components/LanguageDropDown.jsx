import React, { useState } from "react";
import { Menu, MenuItem, Button, Box, Divider } from "@mui/material";
import { useNavigate, useLocation } from "react-router-dom";
import LanguageIcon from "../Assets/language.svg";
import DropdownIcon from "../Assets/dropdown_white.svg";

function LanguageDropdown() {
  const [anchorEl, setAnchorEl] = useState(null);
  const navigate = useNavigate();
  const location = useLocation();

  // Mapping URL prefix to language code
  const pathToLangMap = {
    "/app": "EN",
    "/esapp": "ES",
    "/plapp": "PL",
  };

  const langToPathMap = {
    EN: "/app",
    ES: "/esapp",
    PL: "/plapp",
  };

  // Detect current language from pathname
  const currentPath = location.pathname;
  const currentLang =
    Object.entries(pathToLangMap).find(([prefix]) =>
      currentPath.startsWith(prefix)
    )?.[1] || "EN";

  const allLanguages = [
    { code: "EN", label: "English" },
    { code: "ES", label: "Spanish" },
    { code: "PL", label: "Polish" },
  ];

  const availableLanguages = allLanguages.filter(
    (lang) => lang.code !== currentLang
  );
  const currentLangLabel =
    allLanguages.find((lang) => lang.code === currentLang)?.label || "English";

  const handleClick = (event) => {
    setAnchorEl(event.currentTarget);
  };

  const handleClose = () => {
    setAnchorEl(null);
  };

  const handleLanguageChange = (newLang) => {
    const newPath = langToPathMap[newLang];
    if (newPath) {
      navigate(newPath);
    }
    handleClose();
  };

  return (
    <Box m={0} p={0}>
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
          minWidth: "150px",
          justifyContent: "space-between",
          margin: 0,
        }}
      >
        <img
          src={LanguageIcon}
          alt="Language"
          style={{ width: 20, height: 20, marginRight: 8 }}
        />
        {currentLangLabel}
        <img
          src={DropdownIcon}
          alt="Dropdown"
          style={{ width: 16, height: 16, marginLeft: 8 }}
        />
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
            width: anchorEl ? anchorEl.clientWidth : "auto",
            padding: 0,
          },
        }}
      >
        {availableLanguages.map((lang, index) => (
          <React.Fragment key={lang.code}>
            {index > 0 && <Divider />}
            <MenuItem
              onClick={() => handleLanguageChange(lang.code)}
              sx={{ color: "black" }}
            >
              {lang.label}
            </MenuItem>
          </React.Fragment>
        ))}
      </Menu>
    </Box>
  );
}

export default LanguageDropdown;
