// import React, { useState, useRef, useEffect } from "react";
// import { Grid, Typography, Box } from "@mui/material";
// import Attachment from "./Attachment";
// import ChatInput from "./ChatInput";
// import StreamingResponse from "./StreamingResponse";
// import createMessageBlock from "../utilities/createMessageBlock";
// import { useUser } from "../utilities/UserContext";  // Import the user context
// import { ALLOW_FILE_UPLOAD, ALLOW_VOICE_RECOGNITION, ALLOW_FAQ, CONTACT_US } from "../utilities/constants";
// import BotFileCheckReply from "./BotFileCheckReply";
// import SpeechRecognitionComponent from "./SpeechRecognition";
// import FirstBotMessage from './FirstBotMessage';
// import { CHAT_API } from "../utilities/constants";

// function ChatBody() {
//   const { userData } = useUser(); // Access username and zipcode from the context
//   const [messageList, setMessageList] = useState([]);
//   const [processing, setProcessing] = useState(false);
//   const [message, setMessage] = useState("");
//   const [questionAsked, setQuestionAsked] = useState(false);
//   const messagesEndRef = useRef(null);

//   useEffect(() => {
//     const firstBotMessage = createMessageBlock(
//       <FirstBotMessage language={"en"}/>,
//       "BOT", "TEXT", "RECEIVED"
//     );
    
//     setMessageList([firstBotMessage]);

//     scrollToBottom();
//   }, []);

//   const scrollToBottom = () => {
//     if (messagesEndRef.current) {
//       messagesEndRef.current.scrollIntoView({ behavior: "smooth" });
//     }
//   };

//   const handleSendMessage = (userMessage) => {
//     setProcessing(true);
//     const newMessageBlock = createMessageBlock(userMessage, "USER", "TEXT", "SENT");
  
//     // Hardcoded bot response (from the provided object)
//     const hardcodedBotResponse = {
//       user_id: "test",
//       zipcode: "45786",
//       language: "English",
//       response_data: {
//         zipcode: "45786",
//         service_categories: [
//           "General Assistance",
//           "Social Services",
//           "Community Resources"
//         ],
//         language: "English",
//         source: "Perplexity",
//         services: [
//           {
//             agency: "Monroe Family Pet Hospital",
//             details: {
//               zipcode: "45786",
//               additional_information: "Hours: Mon-Fri 8am-6pm (Tue until 8pm), Sat 9am-1pm (closed 2 Saturdays/month). Phone: Not listed in sources (check website for contact). Services: Full medical/surgical/dental care with orthopedic surgery specialization",
//               hours: "Hours: Mon-Fri 8am-6pm (Tue until 8pm), Sat 9am-1pm (closed 2 Saturdays/month)",
//               address: "301 Heritage Green Dr.",
//               city: "Monroe",
//               phone: "Phone: Not listed in sources (check website for contact)",
//               referral_process: "Call Not listed in sources (check website for contact)",
//               service_category: "Social Services",
//               referral_id: "test",
//               source: "Perplexity AI",
//               state: "OH",
//               id: "4f8ef848-0fac-4ebf-9a20-183f94a93f21"
//             }
//           },
//           {
//             agency: "Monroe Family Pet Hospital",
//             details: {
//               zipcode: "45786",
//               additional_information: "Hours: Mon-Fri 8am-6pm (Tue until 8pm), Sat 9am-1pm (closed 2 Saturdays/month). Phone: Not listed in sources (check website for contact). Services: Full medical/surgical/dental care with orthopedic surgery specialization.",
//               hours: "Mon-Fri 8am-6pm (Tue until 8pm), Sat 9am-1pm (closed 2 Saturdays/month)",
//               address: "3301 Heritage Green Dr.",
//               city: "Monroe",
//               phone: "Phone: Not listed in sources (check website for contact)",
//               referral_process: "Call Not listed in sources (check website for contact)",
//               service_category: "Social Services",
//               referral_id: "test",
//               source: "Perplexity AI",
//               state: "OH",
//               id: "d2a78b38-8cbc-40fc-890c-3743c9dd00c2"
//             }
//           },
//           {
//             agency: "Harrison Animal Hospital",
//             details: {
//               zipcode: "45786",
//               additional_information: "Hours: Not explicitly listed (typical vet hours recommended). Phone: (513) 367-4806. Services: Wellness exams, diagnostics, dental care, and urgent services.",
//               hours: "Hours: Not explicitly listed (typical vet hours recommended)",
//               address: "102 May Dr.",
//               city: "Harrison",
//               phone: "Phone: (513) 367-4806",
//               referral_process: "Call (513) 367-4806",
//               service_category: "Social Services",
//               referral_id: "test",
//               source: "Perplexity AI",
//               state: "OH",
//               id: "your-harrison-hospital-id-here"
//             }
//           }          
//         ],
//         message: "Here are Social Services services in 45786 for Pet health classes and educational events",
//         status: "success"



//       }
//     };

//     const botReply = (
//       <BotReplyMessage hardcodedBotResponse={hardcodedBotResponse} />
//     );
  
//     const botReplyMessage = createMessageBlock(
//       botReply,
//       "BOT",
//       "TEXT",
//       "RECEIVED"
//     );
  
//     setMessageList((prevList) => [...prevList, newMessageBlock, botReplyMessage]);
    
//     setProcessing(false);
//     setQuestionAsked(true);
//   };

//   const handleFileUploadComplete = (file, fileStatus) => {
//     const newMessageBlock = createMessageBlock(`File uploaded: ${file.name}`, "USER", "FILE", "SENT", file.name, fileStatus);
//     setMessageList((prevList) => [...prevList, newMessageBlock]);
//     setQuestionAsked(true);

//     setTimeout(() => {
//       const botMessageBlock = createMessageBlock(fileStatus === "File page limit check succeeded." ? "Checking file size." : fileStatus === "File size limit exceeded." ? "File size limit exceeded. Please upload a smaller file." : "Network Error. Please try again later.", "BOT", "FILE", "RECEIVED", file.name, fileStatus);
//       setMessageList((prevList) => [...prevList, botMessageBlock]);
//     }, 1000);
//   };

//   const handlePromptClick = (prompt) => {
//     handleSendMessage(prompt);
//   };

//   const getMessage = () => message;

//   return (
//     <>
//       <Box display="flex" flexDirection="column" justifyContent="space-between" overflow="auto" sx={{ height: "100vh" }}>
//         {/* Chat Container */}
//         <Box flex={1} overflow="auto" sx={{ paddingBottom: "60px" }} className="chatScrollContainer">
//           {messageList.map((msg, index) => (
//             <Box key={index} mb={2}>
//               {msg.sentBy === "USER" ? (
//                 <UserReply message={msg.message} />
//               ) : msg.sentBy === "BOT" && msg.state === "PROCESSING" ? (
//                 <StreamingResponse initialMessage={msg.message} setProcessing={setProcessing} />
//               ) : (
//                 <BotFileCheckReply message={msg.message} fileName={msg.fileName} fileStatus={msg.fileStatus} messageType={msg.sentBy === "USER" ? "user_doc_upload" : "bot_response"} />
//               )}
//             </Box>
//           ))}
//           <div ref={messagesEndRef} />
//         </Box>

//         {/* Chat Input */}
//         <Box display="flex" justifyContent="space-between" alignItems="flex-end" sx={{ flexShrink: 0, position: "fixed", bottom: 0, width: "60%", padding: "10px 20px", backgroundColor: "white" }}>
//           <Box sx={{ display: ALLOW_VOICE_RECOGNITION ? "flex" : "none" }}>
//             <SpeechRecognitionComponent setMessage={setMessage} getMessage={getMessage} />
//           </Box>
//           <Box sx={{ display: ALLOW_FILE_UPLOAD ? "flex" : "none" }}>
//             <Attachment onFileUploadComplete={handleFileUploadComplete} />
//           </Box>
//           <Box sx={{ width: "100%" }} ml={2}>
//             <ChatInput onSendMessage={handleSendMessage} processing={processing} message={message} setMessage={setMessage} language={{language}} />
//           </Box>
//         </Box>
//       </Box>
//     </>
//   );
// }

// export default ChatBody;

// // BotReplyMessage component to display formatted response
// function BotReplyMessage({ hardcodedBotResponse }) {
//   return (
//     <Box>
//       <Typography variant="h6" sx={{ fontWeight: "bold" }}>
//       <strong>{hardcodedBotResponse.response_data.message}</strong>
//       </Typography>
//       <Typography variant="body1" paragraph>
//       (Source: {hardcodedBotResponse.response_data.source})
//       </Typography>
//       {hardcodedBotResponse.response_data.services.map((service, index) => (
//         <Box key={service.id}>
//           <Typography variant="body1" paragraph>
//             <strong>{`${index + 1}. Agency: ${service.agency}`}</strong>
//           </Typography>
//           <Typography variant="body2" paragraph>
//             <strong>Address:</strong> {service.details.address}, {service.details.city}
//           </Typography>
//           <Typography variant="body2" paragraph>
//             <strong>Phone:</strong> {service.details.phone}
//           </Typography>
//           <Typography variant="body2" paragraph>
//             <strong>Hours:</strong> {service.details.hours}
//           </Typography>
//           <Typography variant="body2" paragraph>
//             <strong>Additional Information:</strong> {service.details.additional_information}
//           </Typography>
//           <Typography variant="body2" paragraph>
//             <strong>Referral Process:</strong> {service.details.referral_process}
//           </Typography>
//         </Box>
//       ))}
//     </Box>
//   );
// }

// function UserReply({ message }) {
//   return (
//     <Grid container direction="row" justifyContent="flex-end" alignItems="flex-end" >
//       <Grid item className="userMessage" padding={3} sx={{ backgroundColor: (theme) => theme.palette.background.userMessage }}>
//         <Typography variant="body1" sx={{ fontSize: '1.2 rem'}}>
//           {message}
//         </Typography>
//       </Grid>
//     </Grid>
//   );
// }


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

function ChatBody() {
  const { userData } = useUser();
  const [messageList, setMessageList] = useState([]);
  const [processing, setProcessing] = useState(false);
  const [message, setMessage] = useState("");
  const [questionAsked, setQuestionAsked] = useState(false);
  const messagesEndRef = useRef(null);

  useEffect(() => {
    const firstBotMessage = createMessageBlock(
      <FirstBotMessage language="en" />,
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

  const handleSendMessage = (message) => {
    setProcessing(true);
    const newMessageBlock = createMessageBlock(message, "USER", "TEXT", "SENT");
    setMessageList((prevList) => [...prevList, newMessageBlock]);
    getBotResponse(setMessageList, setProcessing, message, userData.username, userData.zipcode);
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
    <Box display="flex" flexDirection="column" justifyContent="space-between" overflow="auto" sx={{ height: "100vh" }}>
      <Box flex={1} overflow="auto" sx={{ paddingBottom: "60px" }} className="chatScrollContainer">
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

      <Box display="flex" justifyContent="space-between" alignItems="flex-end" sx={{ flexShrink: 0, position: "fixed", bottom: 0, width: "60%", padding: "10px 20px", backgroundColor: "white" }}>
        {ALLOW_VOICE_RECOGNITION && (
          <SpeechRecognitionComponent setMessage={setMessage} getMessage={getMessage} />
        )}
        {ALLOW_FILE_UPLOAD && (
          <Attachment onFileUploadComplete={handleFileUploadComplete} />
        )}
        <Box sx={{ width: "100%" }} ml={2}>
          <ChatInput onSendMessage={handleSendMessage} processing={processing} message={message} setMessage={setMessage} />
        </Box>
      </Box>
    </Box>
  );
}

export default ChatBody;

function UserReply({ message }) {
  return (
    <Grid container direction="row" justifyContent="flex-end" alignItems="flex-end">
      <Grid item className="userMessage" padding={3} sx={{ backgroundColor: (theme) => theme.palette.background.userMessage }}>
        <Typography variant="body1" sx={{ fontSize: '1.2rem' }}>
          {message}
        </Typography>
      </Grid>
    </Grid>
  );
}

const getBotResponse = (setMessageList, setProcessing, message, username, zipcode) => {
  const processingMessageBlock = createMessageBlock("Thinking...", "BOT", "TEXT", "PROCESSING");
  setMessageList((prevList) => [...prevList, processingMessageBlock]);

  const socket = new WebSocket(CHAT_API);

  socket.onopen = () => {
    const payload = {
      action: "query",
      user_id: username || "anonymous",
      zipcode: zipcode || "00000",
      user_query: message,
      language: "english"
    };
    socket.send(JSON.stringify(payload));
    console.log("📤 Sending request:", payload);
  };

  socket.onmessage = (event) => {
    const data = JSON.parse(event.data);
    console.log("📩 Received response:", data);

    if (data?.response_data?.services) {
      const { message: mainMessage, services } = data.response_data;

      const servicesUI = services.map(service => (
        <div key={service.id} style={{ marginBottom: '20px' }}>
          <Typography variant="h6" sx={{ fontWeight: 'bold' }}>{service.agency}</Typography>
          <Typography><strong>Referral Process:</strong> {service.details.referral_process}</Typography>
          <Typography><strong>Hours:</strong> {service.details.hours}</Typography>
          <Typography><strong>Phone:</strong> {service.details.phone}</Typography>
          <Typography><strong>Address:</strong> {`${service.details.address}, ${service.details.city}, ${service.details.state} ${service.details.zipcode}`}</Typography>
          <Typography><strong>Additional Info:</strong> {service.details.additional_information}</Typography>
        </div>
      ));

      const botMessageBlock = createMessageBlock(
        <div>
          <Typography variant="h6" sx={{ fontWeight: 'bold' }}>{mainMessage}</Typography>
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
      setMessageList((prevList) => [
        ...prevList,
        createMessageBlock("Sorry, I couldn't understand that.", "BOT", "TEXT", "RECEIVED")
      ]);
    }

    setProcessing(false);
    socket.close();
  };

  socket.onerror = () => {
    setMessageList((prevList) => [
      ...prevList,
      createMessageBlock("An error occurred. Please try again later.", "BOT", "TEXT", "RECEIVED")
    ]);
    setProcessing(false);
  };

  socket.onclose = (event) => {
    if (!event.wasClean) {
      console.error("WebSocket closed unexpectedly");
    }
  };
};

