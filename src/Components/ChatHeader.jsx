import React from "react";
import Typography from "@mui/material/Typography";
import { useLanguage } from "../utilities/LanguageContext"; // Adjust the import path
import { TEXT, HEADER_TEXT_GRADIENT } from "../utilities/constants"; // Adjust the import path
import { Container } from "@mui/material";
import { useLocation } from "react-router-dom"; // <-- Import location hook

function ChatHeader({ selectedLanguage }) {
  const { language: contextLanguage } = useLanguage();
  // const language = selectedLanguage || contextLanguage || 'EN'; // Use selectedLanguage if provided, otherwise default to contextLanguage or 'EN'
  const location = useLocation(); // <-- Get current path

  const path = location.pathname;
  let lang = "EN";
  if (path.startsWith("/esapp")) {
    lang = "ES";
  } else if (path.startsWith("/plapp")) {
    lang = "PL";
  }
  return (
    <Container
      sx={{
        display: 'flex',
        justifyContent: 'center',
        alignItems: 'center',
        height: '100%',
      }}
    >
      <Typography
        variant="h5"
        className="chatHeaderText"
        sx={{ fontWeight: "bold", 
          color: "#1F1463",
        }}
        // sx={{
        //   backgroundClip: 'text', // Apply the gradient to the text
        //   color: 'transparent', // Make the text transparent so the gradient shows
        //   background: HEADER_TEXT_GRADIENT, // The gradient will be applied to the text
        //   textAlign: 'left',
        // }}
      >
        {TEXT[lang]?.CHAT_HEADER_TITLE || "Default Chat Header Title"} {/* Safe fallback */}
      </Typography>
      
    </Container>
  );
}

export default ChatHeader;
