import React, { useState, useRef, useEffect } from "react";
import { Grid, Typography, Box } from "@mui/material";
import ChatInput from "./ChatInput";
import StreamingResponse from "./StreamingResponse";
import createMessageBlock from "../utilities/createMessageBlock";
import { useUser } from "../utilities/UserContext";
import { ALLOW_FILE_UPLOAD, ALLOW_VOICE_RECOGNITION } from "../utilities/constants";
import FirstBotMessage from './FirstBotMessage';
import { CHAT_API } from "../utilities/constants";
import { useLocation } from "react-router-dom"; // <-- Import location hook
import BotFileCheckReply from "./BotFileCheckReply";

const translations = {
  EN: {
    networkError: "Network Error. Please try again later.",
    thinking: "Thinking...",
    errorProcessing: "There was an error processing your request. Please try again.",
    noUnderstanding: "Sorry, I couldn't understand that.",
    prefixText: "I could not find relevant information in our database, but here is what I could find on the internet.\n\n",
    referralProcess: "Referral Process:",
    hours: "Hours:",
    phone: "Phone:",
    address: "Address:",
    additionalInfo: "Additional Info:"
  },
  ES: {
    networkError: "Error de red. Por favor, inténtalo de nuevo más tarde.",
    thinking: "Pensando...",
    errorProcessing: "Hubo un error al procesar tu solicitud. Por favor, inténtalo de nuevo.",
    noUnderstanding: "Lo siento, no pude entender eso.",
    prefixText: "No pude encontrar información relevante en nuestra base de datos, pero esto es lo que encontré en internet.\n\n",
    referralProcess: "Proceso de Referencia:",
    hours: "Horario:",
    phone: "Teléfono:",
    address: "Dirección:",
    additionalInfo: "Información Adicional:"
  },
  PL: {
    networkError: "Błąd sieci. Spróbuj ponownie później.",
    thinking: "Myślę...",
    errorProcessing: "Wystąpił błąd podczas przetwarzania twojego żądania. Spróbuj ponownie.",
    noUnderstanding: "Przepraszam, nie mogłem tego zrozumieć.",
    prefixText: "Nie znalazłem odpowiednich informacji w naszej bazie danych, ale oto co znalazłem w internecie.\n\n",
    referralProcess: "Proces skierowania:",
    hours: "Godziny:",
    phone: "Telefon:",
    address: "Adres:",
    additionalInfo: "Dodatkowe informacje:"
  }
};

function ChatBody( language ) {

  const { userData } = useUser();

  console.log('userData:', userData);

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
    getBotResponse(setMessageList, setProcessing, msg, userData.user_id, userData.zipcode, language, lang);
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
  sx={{
    height: '100vh',
    overflow: 'hidden', // ensure children don’t overflow
  }}
>



<Box
  flex={1}
  overflow="auto"
  className="chatScrollContainer"
  sx={{
    pb: '100px', // enough space to avoid input overlay
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
  sx={{
    position: 'fixed',
    width:"60%",
    bottom: 0,
    backgroundColor: 'white',
    borderTop: '1px solid #ccc',
    px: 2,
    py: 1,
    zIndex: 1000,
  }}
>
  <ChatInput
    onSendMessage={handleSendMessage}
    processing={processing}
    message={message}
    setMessage={setMessage}
    language={lang} // make sure this passes correctly
  />
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

const getBotResponse = (setMessageList, setProcessing, message, username, zipcode, language, lang ) => {
  const t = translations[lang];
  const processingMessageBlock = createMessageBlock(t.thinking, "BOT", "TEXT", "PROCESSING");
  setMessageList((prevList) => [...prevList, processingMessageBlock]);


  const socket = new WebSocket(CHAT_API);

  socket.onopen = () => {
    const payload = {
      action: "query",
      user_id: username,
      zipcode: zipcode,
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
            ? createMessageBlock(t.errorProcessing, "BOT", "TEXT", "RECEIVED")
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
      const { message: mainMessage, services, source } = data.response_data || {};
    
      let prefixText = "";
      if (source && source.toLowerCase().includes("perplexity")) {
        prefixText = t.prefixText;
      }
    
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
              {referral_process && <Typography><strong>{t.referralProcess}</strong> {referral_process}</Typography>}
              {hours && <Typography><strong>{t.hours}</strong> {hours}</Typography>}
              {phone && <Typography><strong>{t.phone}</strong> {phone}</Typography>}
              {(address || city || state || zipcode) && (
                <Typography>
                  <strong>{t.address}</strong> {`${address || ""}, ${city || ""}, ${state || ""} ${zipcode || ""}`}
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
            <Typography variant="h6" sx={{ fontWeight: 'bold' }}>
              {prefixText}{mainMessage}
            </Typography>
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
