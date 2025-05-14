import React, { useState, useRef, useEffect } from "react";
import { Grid, Typography, Box } from "@mui/material";
import Attachment from "./Attachment";
import ChatInput from "./ChatInput";
import StreamingResponse from "./StreamingResponse";
import createMessageBlock from "../utilities/createMessageBlock";
import { useUser } from "../utilities/UserContext";
import { ALLOW_FILE_UPLOAD, ALLOW_VOICE_RECOGNITION } from "../utilities/constants";
import BotFileCheckReply from "./BotFileCheckReply";
import SpeechRecognitionComponent from "./SpeechRecognition";
import FirstBotMessage from './FirstBotMessage';
import { CHAT_API } from "../utilities/constants";
import { useLocation } from "react-router-dom"; // <-- Import location hook

function ChatBody( language ) {
  const { userData } = useUser();
  const [messageList, setMessageList] = useState([]);
  const [processing, setProcessing] = useState(false);
  const [message, setMessage] = useState("");
  const [questionAsked, setQuestionAsked] = useState(false);
  const messagesEndRef = useRef(null);
  const location = useLocation(); // <-- Get current path

  // === Determine language from path ===
  const path = location.pathname;
  let lang = "EN";
  if (path.startsWith("/esapp")) {
    lang = "ES";
  } else if (path.startsWith("/plapp")) {
    lang = "PL";
  }

  useEffect(() => {
    const firstBotMessage = createMessageBlock(
      <FirstBotMessage language={lang} />,
      "BOT", "TEXT", "RECEIVED"
    );
    setMessageList([firstBotMessage]);
    scrollToBottom();
  }, []);

  const scrollToBottom = () => {
    if (messagesEndRef.current) {
      messagesEndRef.current.scrollIntoView({ behavior: "smooth" });
    }
  };

  const handleSendMessage = (msg) => {
    if (processing) return; // Prevent sending new messages while processing
    setProcessing(true);
    const newMessageBlock = createMessageBlock(msg, "USER", "TEXT", "SENT");
    setMessageList((prevList) => [...prevList, newMessageBlock]);
    getBotResponse(setMessageList, setProcessing, msg, userData.username, userData.zipcode, language);
    setQuestionAsked(true);
  };

  const handleFileUploadComplete = (file, fileStatus) => {
    const newMessageBlock = createMessageBlock(`File uploaded: ${file.name}`, "USER", "FILE", "SENT", file.name, fileStatus);
    setMessageList((prevList) => [...prevList, newMessageBlock]);
    setQuestionAsked(true);

    setTimeout(() => {
      const botMessageBlock = createMessageBlock(
        fileStatus === "File page limit check succeeded."
          ? "Checking file size."
          : fileStatus === "File size limit exceeded."
          ? "File size limit exceeded. Please upload a smaller file."
          : "Network Error. Please try again later.",
        "BOT", "FILE", "RECEIVED", file.name, fileStatus
      );
      setMessageList((prevList) => [...prevList, botMessageBlock]);
    }, 1000);
  };

  const handlePromptClick = (prompt) => {
    handleSendMessage(prompt);
  };

  const getMessage = () => message;

  return (
    <Box
  display="flex"
  flexDirection="column"
  justifyContent="space-between"
  sx={{
    height: "100vh",
    overflow: "hidden",
    px: { xs: 1, sm: 2, md: 3 },
  }}
>

<Box
  flex={1}
  overflow="auto"
  className="chatScrollContainer"
  sx={{
    pb: { xs: "120px", sm: "80px" }, // More padding for mobile keyboards
  }}
>

        {messageList.map((msg, index) => (
          <Box key={index} mb={2}>
            {msg.sentBy === "USER" ? (
              <UserReply message={msg.message} />
            ) : msg.sentBy === "BOT" && msg.state === "PROCESSING" ? (
              <StreamingResponse initialMessage={msg.message} setProcessing={setProcessing} />
            ) : (
              <BotFileCheckReply message={msg.message} fileName={msg.fileName} fileStatus={msg.fileStatus} messageType={msg.sentBy === "USER" ? "user_doc_upload" : "bot_response"} />
            )}
          </Box>
        ))}
        <div ref={messagesEndRef} />
      </Box>

      <Box
        display="flex"
        flexWrap="wrap"
        justifyContent="space-between"
        alignItems="flex-end"
        sx={{
          flexShrink: 0,
          position: "fixed",
          bottom: 0,
          width: '100%',
          px: 2,
          py: 1,
          backgroundColor: "white",
          zIndex: 10
        }}
      >
        <Box
          sx={{
            display: "flex",
            alignItems: "center",
            width: { xs: '100%', sm: 'auto' },
            flexWrap: "wrap",
            gap: 1,
            mb: { xs: 1, sm: 0 }
          }}
        >
          {ALLOW_VOICE_RECOGNITION && (
            <SpeechRecognitionComponent setMessage={setMessage} getMessage={getMessage} />
          )}
          {ALLOW_FILE_UPLOAD && (
            <Attachment onFileUploadComplete={handleFileUploadComplete} />
          )}
        </Box>
        <Box sx={{ flexGrow: 1, width: { xs: '100%', sm: 'auto' }, p: 1 }}>
  <ChatInput
    onSendMessage={handleSendMessage}
    processing={processing}
    message={message}
    setMessage={setMessage}
    language
  />
</Box>

      </Box>

    </Box>
  );
}

export default ChatBody;

function parseMarkdownBold(text) {
  if (!text) return null;
  const parts = text.split(/\*\*(.*?)\*\*/g); // Split by **bold**
  return parts.map((part, index) =>
    index % 2 === 1 ? <strong key={index}>{part}</strong> : part
  );
}

function UserReply({ message }) {
  return (
    <Grid
  container
  direction="row"
  justifyContent="flex-end"
  alignItems="flex-end"
  sx={{ maxWidth: '100%' }}
>
  <Grid
    item
    sx={{
      backgroundColor: (theme) => theme.palette.background.userMessage,
      borderRadius: 2,
      px: 2,
      py: 1,
      maxWidth: { xs: '80%', sm: '60%', md: '50%' },
      wordWrap: 'break-word',
    }}
  >
    <Typography variant="body2" sx={{ fontSize: '1rem' }}>
      {message}
    </Typography>
  </Grid>
</Grid>

  );
}

const getBotResponse = (setMessageList, setProcessing, message, username, zipcode, language) => {
  const processingMessageBlock = createMessageBlock("Thinking...", "BOT", "TEXT", "PROCESSING");
  setMessageList((prevList) => [...prevList, processingMessageBlock]);

  const socket = new WebSocket(CHAT_API);

  socket.onopen = () => {
    const payload = {
      action: "query",
      user_id: username || "user",
      zipcode: zipcode || "62701",
      user_query: message,
      language: language.language|| "english"
    };
    console.log("language, ", language);
    console.log("language, ", language.language);
    socket.send(JSON.stringify(payload));
    console.log("📤 Sending request:", payload);
  };

  socket.onmessage = (event) => {
    let data;

    try {
      const parsed = JSON.parse(event.data);
      data = typeof parsed.body === "string" ? JSON.parse(parsed.body) : parsed;
    } catch (error) {
      console.error("❌ Failed to parse WebSocket message:", error, event.data);
      setMessageList((prevList) =>
        prevList.map((msg) =>
          msg.state === "PROCESSING"
            ? createMessageBlock("There was an error processing your request. Please try again.", "BOT", "TEXT", "RECEIVED")
            : msg
        )
      );
      setProcessing(false);
      socket.close();
      return;
    }

    console.log("📩 Received parsed response:", data);

    const status = data?.status?.toLowerCase();

    if (status === "processing" || status === "searching") {
      // Do not display or update UI for these states.
      return;
    }

    if (status === "complete" || status == "success") {
      const { message: mainMessage, services } = data.response_data || {};

      if (services && Array.isArray(services)) {
        const servicesUI = services.map((service) => {
          const { agency, details = {}, address, city, state, zipcode } = service;
          const {
            referral_process,
            hours,
            phone,
            additional_information
          } = details;

          return (
            <Box key={service.id || Math.random()} sx={{ mb: 3 }}>
              {agency && <Typography variant="h6" sx={{ fontWeight: 'bold' }}>{agency}</Typography>}
              {referral_process && <Typography><strong>Referral Process:</strong> {referral_process}</Typography>}
              {hours && <Typography><strong>Hours:</strong> {hours}</Typography>}
              {phone && <Typography><strong>Phone:</strong> {phone}</Typography>}
              {(address || city || state || zipcode) && (
                <Typography>
                  <strong>Address:</strong> {`${address || ""}, ${city || ""}, ${state || ""} ${zipcode || ""}`}
                </Typography>
              )}
              {additional_information && (
                <Typography><strong>Additional Info:</strong> {parseMarkdownBold(additional_information)}</Typography>
              )}
            </Box>
          );
        });

        const botMessageBlock = createMessageBlock(
          <div>
            <Typography variant="h6" sx={{ fontWeight: 'bold' }}>{mainMessage}</Typography>
            {servicesUI}
          </div>,
          "BOT", "TEXT", "RECEIVED"
        );

        // Replace "Thinking..." message
        setMessageList((prevList) =>
          prevList.map((msg) =>
            msg.state === "PROCESSING" ? botMessageBlock : msg
          )
        );
      } else {
        // Response doesn't contain expected structure
        setMessageList((prevList) =>
          prevList.map((msg) =>
            msg.state === "PROCESSING"
              ? createMessageBlock("Sorry, I couldn't understand that.", "BOT", "TEXT", "RECEIVED")
              : msg
          )
        );
      }

      setProcessing(false);
      socket.close();
    } else if (status == "error") {
      // Invalid status or error case
      setMessageList((prevList) =>
        prevList.map((msg) =>
          msg.state === "PROCESSING"
            ? createMessageBlock("There was some issue processing your request. Please try again.", "BOT", "TEXT", "RECEIVED")
            : msg
        )
      );
      setProcessing(false);
      socket.close();
    }
  };

  socket.onerror = () => {
    setMessageList((prevList) =>
      prevList.map((msg) =>
        msg.state === "PROCESSING"
          ? createMessageBlock("There was some issue processing your request. Please try again.", "BOT", "TEXT", "RECEIVED")
          : msg
      )
    );
    setProcessing(false);
  };

  socket.onclose = (event) => {
    if (!event.wasClean) {
      console.error("⚠️ WebSocket closed unexpectedly");
    }
  };
};
