import React, { useState, useRef, useEffect } from "react";
import { Grid, Typography, Box } from "@mui/material";
import ChatInput from "./ChatInput";
import StreamingResponse from "./StreamingResponse";
import createMessageBlock from "../utilities/createMessageBlock";
import { useUser } from "../utilities/UserContext";
import { ALLOW_FILE_UPLOAD, ALLOW_VOICE_RECOGNITION } from "../utilities/constants";
import FirstBotMessage from './FirstBotMessage';
import { CHAT_API } from "../utilities/constants";
import { useLocation } from "react-router-dom";
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
    additionalInfo: "Additional Info:",
    processing: "Processing your request...",
    searching: "Searching for relevant information...",
    analyzing: "Analyzing results...",
    connecting: "Connecting to services..."
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
    additionalInfo: "Información Adicional:",
    processing: "Procesando tu solicitud...",
    searching: "Buscando información relevante...",
    analyzing: "Analizando resultados...",
    connecting: "Conectando a servicios..."
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
    additionalInfo: "Dodatkowe informacje:",
    processing: "Przetwarzanie twojego żądania...",
    searching: "Wyszukiwanie odpowiednich informacji...",
    analyzing: "Analizowanie wyników...",
    connecting: "Łączenie z usługami..."
  }
};

// ✅ DEFINE ProcessingMessage COMPONENT FIRST
const ProcessingMessage = ({ message }) => {
  const [dots, setDots] = useState("");

  useEffect(() => {
    const interval = setInterval(() => {
      setDots(prev => {
        if (prev === "...") return "";
        return prev + ".";
      });
    }, 500);

    return () => clearInterval(interval);
  }, []);

  return (
    <Box
      sx={{
        display: 'flex',
        alignItems: 'center',
        fontStyle: 'italic',
        color: '#666',
        padding: '8px 0'
      }}
    >
      <Typography variant="body1" component="span">
        {message}
      </Typography>
      <Typography
        component="span"
        sx={{
          display: 'inline-block',
          width: '20px',
          textAlign: 'left',
          fontSize: '1.2em',
          fontWeight: 'bold'
        }}
      >
        {dots}
      </Typography>
    </Box>
  );
};

function ChatBody(language) {
  const { userData } = useUser();


  // Helper function to get the user identifier
  const getUserIdentifier = () => {
    const username = userData?.username?.toString().trim();
    const user_id = userData?.user_id?.toString().trim();

    const identifier = username || user_id || null;
    return identifier;
  };

  const [messageList, setMessageList] = useState([]);
  const [processing, setProcessing] = useState(false);
  const [message, setMessage] = useState("");
  const [questionAsked, setQuestionAsked] = useState(false);
  const messagesEndRef = useRef(null);
  const location = useLocation();

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
    if (processing) return;
    setProcessing(true);
    const newMessageBlock = createMessageBlock(msg, "USER", "TEXT", "SENT");
    setMessageList((prevList) => [...prevList, newMessageBlock]);

    const userIdentifier = getUserIdentifier();
    const userZipcode = userData?.zipcode;


    getBotResponse(
      setMessageList,
      setProcessing,
      msg,
      userIdentifier,
      userZipcode,
      language,
      lang
    );
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
        overflow: 'hidden',
      }}
    >
      <Box
        flex={1}
        overflow="auto"
        className="chatScrollContainer"
        sx={{
          pb: '100px',
        }}
      >
        {messageList.map((msg, index) => (
          <Box key={index} mb={2}>
            {msg.sentBy === "USER" ? (
              <UserReply message={msg.message} />
            ) : msg.sentBy === "BOT" && msg.state === "PROCESSING" ? (
              // ✅ FIXED: Use our own processing component instead of StreamingResponse
              <BotProcessingReply message={msg.message} />
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
          width: "60%",
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
          language={lang}
        />
      </Box>
    </Box>
  );
}

export default ChatBody;

function parseMarkdownBold(text) {
  if (!text) return null;
  const parts = text.split(/\*\*(.*?)\*\*/g);
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

// ✅ NEW: Bot processing reply component (replaces StreamingResponse for processing)
function BotProcessingReply({ message }) {
  return (
    <Grid
      container
      direction="row"
      justifyContent="flex-start"
      alignItems="flex-end"
      sx={{ maxWidth: '100%' }}
    >
      <Grid
        item
        sx={{
          backgroundColor: (theme) => theme.palette.background.botMessage || '#f5f5f5',
          borderRadius: 2,
          px: 2,
          py: 1,
          maxWidth: { xs: '80%', sm: '60%', md: '50%' },
          wordWrap: 'break-word',
        }}
      >
        {/* Render the ProcessingMessage component or regular text */}
        {typeof message === 'string' ? (
          <ProcessingMessage message={message} />
        ) : (
          message
        )}
      </Grid>
    </Grid>
  );
}

const getBotResponse = (setMessageList, setProcessing, message, userIdentifier, zipcode, language, lang) => {
  const t = translations[lang];

  // ✅ Create initial processing message with unique ID for tracking
  const processingId = Date.now();
  const processingMessageBlock = createMessageBlock(
    t.thinking,
    "BOT",
    "TEXT",
    "PROCESSING"
  );
  processingMessageBlock.id = processingId; // Add unique ID

  setMessageList((prevList) => [...prevList, processingMessageBlock]);

  const socket = new WebSocket(CHAT_API);

  socket.onopen = () => {
    const payload = {
      action: "query",
      user_id: userIdentifier,
      zipcode: zipcode,
      user_query: message,
      language: language?.language || "english"
    };

    socket.send(JSON.stringify(payload));
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


    const status = data?.status?.toLowerCase();

    // ✅ ENHANCED: Handle processing/searching states with real-time updates
    if (status === "processing" || status === "searching") {
      const serverMessage = data?.message || data?.response_data?.message;

      let processingMessage;
      if (serverMessage) {
        processingMessage = serverMessage;
      } else {
        processingMessage = t[status] || t.processing;
      }


      setMessageList((prevList) => {
        const updatedList = prevList.map((msg, index) => {
          if (msg.state === "PROCESSING") {
            return createMessageBlock(
              processingMessage,
              "BOT",
              "TEXT",
              "PROCESSING"
            );
          }
          return msg;
        });

        return updatedList;
      });

      // ✅ Force scroll to bottom after update
      setTimeout(() => {
        const container = document.querySelector('.chatScrollContainer');
        if (container) {
          container.scrollTop = container.scrollHeight;
        }
      }, 50);

      return; // Continue waiting for more updates
    }

    // ✅ Handle final completion
    if (status === "complete" || status === "success") {
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
                <Typography><strong>{t.additionalInfo}</strong> {parseMarkdownBold(additional_information)}</Typography>
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

        setMessageList((prevList) =>
          prevList.map((msg) =>
            msg.state === "PROCESSING" ? botMessageBlock : msg
          )
        );
      } else {
        setMessageList((prevList) =>
          prevList.map((msg) =>
            msg.state === "PROCESSING"
              ? createMessageBlock(mainMessage || t.noUnderstanding, "BOT", "TEXT", "RECEIVED")
              : msg
          )
        );
      }

      setProcessing(false);
      socket.close();
    }

    // ✅ Handle error states
    if (status === "error" || status === "failed") {
      const errorMessage = data?.message || data?.response_data?.message || t.errorProcessing;

      setMessageList((prevList) =>
        prevList.map((msg) =>
          msg.state === "PROCESSING"
            ? createMessageBlock(errorMessage, "BOT", "TEXT", "RECEIVED")
            : msg
        )
      );
      setProcessing(false);
      socket.close();
    }
  };

  socket.onerror = (error) => {
    console.error("❌ WebSocket Error:", error);
    setMessageList((prevList) =>
      prevList.map((msg) =>
        msg.state === "PROCESSING"
          ? createMessageBlock(t.networkError, "BOT", "TEXT", "RECEIVED")
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