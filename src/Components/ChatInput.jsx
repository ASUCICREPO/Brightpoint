import React, { useState, useEffect } from "react";
import { TextField, Grid, IconButton } from "@mui/material";
import SendIcon from "@mui/icons-material/Send";
import { useLanguage } from "../utilities/LanguageContext";
import { CHAT_INPUT_PLACEHOLDER, TEXT } from "../utilities/constants";
import { useTranscript } from "../utilities/TranscriptContext";

function ChatInput({ onSendMessage, processing }) {
  const [message, setMessage] = useState("");
  const [helperText, setHelperText] = useState("");
  const { language } = useLanguage();
  const { transcript, setTranscript, isListening } = useTranscript();

  useEffect(() => {
    if (!isListening && transcript) {
      setMessage(prevMessage => prevMessage ? `${prevMessage} ${transcript}` : transcript);
      setTranscript(""); // Clear the transcript buffer
    }
  }, [isListening, transcript, setTranscript]);

  const handleTyping = (event) => {
    if (helperText) {
      setHelperText("");
    }
    setMessage(event.target.value);
  };

  const handleSendMessage = () => {
    if (message.trim() !== "") {
      onSendMessage(message);
      setMessage("");
    } else {
      setHelperText(TEXT["EN"].HELPER_TEXT);
    }
  };

  const getMessage = (message, transcript, isListening) => {
    if (isListening) {
      if (transcript.length) {
        return message.length ? `${message} ${transcript}` : transcript;
      }
    }
    return message;
  };


  return (
    <Grid container item xs={12} alignItems="center" justifyContent="center" sx={{ backgroundColor: "#F9F8FF", paddingLeft: "10px" , borderRadius:"30px"}}>
      <Grid item  sx={{ display: "flex", alignItems: "center", width: "100%", borderRadius:"30px"}}>
        <TextField
          multiline
          maxRows={4}
          fullWidth
          disabled={isListening}
          placeholder={TEXT["EN"].CHAT_INPUT_PLACEHOLDER}
          id="USERCHATINPUT"
          value={getMessage(message, transcript, isListening)}
          onKeyDown={(e) => {
            if (e.key === "Enter" && !e.shiftKey && !processing) {
              e.preventDefault();
              handleSendMessage();
            }
          }}
          onChange={handleTyping}
          helperText={isListening ? TEXT["EN"].SPEECH_RECOGNITION_HELPER_TEXT : helperText}
          sx={{
            backgroundColor: "#F9F8FF",
            borderRadius: "30px",
            "& fieldset": { border: "none" },
            padding: "0"
          }}
        />
        <IconButton
          aria-label="send"
          disabled={processing || isListening}
          onClick={handleSendMessage}
          sx={{
            marginLeft: "8px",
            borderRadius: "50%",
            backgroundColor: "#F9F8FF",
            border: "2px solid #F9F8FF",
            color: (theme) => theme.palette.primary.main, // Set the icon color to primary color
            "&:hover": {
              backgroundColor: "#EAE6FF",
              color: (theme) => theme.palette.primary.dark, // Darker shade of primary on hover
            }
          }}
        >
          <SendIcon />
        </IconButton>
      </Grid>
    </Grid>
  );
}

export default ChatInput;
