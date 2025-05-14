import React, { useState, useEffect, useRef } from "react";
import { Grid, Avatar, Typography } from "@mui/material";
import botAvatar from "../Assets/botAvatar.gif";
import { CHAT_API, ALLOW_MARKDOWN_BOT } from "../utilities/constants";
import ReactMarkdown from "react-markdown";

const StreamingMessage = ({ initialMessage, setProcessing }) => {
  const [responses, setResponses] = useState([]);
  const ws = useRef(null);
  const messageBuffer = useRef(""); // Buffer to hold incomplete JSON strings

  useEffect(() => {
    // Initialize WebSocket connection
    ws.current = new WebSocket(CHAT_API);

    ws.current.onopen = () => {
      // console.log("✅ WebSocket Connected");

      // Construct message payload
      const messagePayload = {
        action: "query",
        user_id: "user_ab",
        zipcode: "61820",
        user_query: initialMessage,
      };

      // ws.current.send(JSON.stringify(messagePayload));
    };

    ws.current.onmessage = (event) => {
      try {
        messageBuffer.current += event.data; // Append new data to buffer
        const parsedData = JSON.parse(messageBuffer.current); // Try parsing the full buffer
    
    
        if (parsedData.status === "success" && parsedData.response_data) {
          const { message, services } = parsedData.response_data;
    
          // Extract service details
          const serviceDetails = services.map(service => 
            `**${service.agency}**\n📍 Address: ${service.address}, ${service.city}, ${service.state} ${service.zipcode}\n📞 Phone: ${service.phone}\nℹ️ Details: ${service.details.additional_information}\n🕒 Hours: ${service.hours}\n🔄 Referral Process: ${service.referral_process}\n`
          ).join("\n\n");
    
          // Combine everything into one message
          const fullMessage = `**${message}**\n\n${serviceDetails}`;
    
          setResponses((prev) => [...prev, fullMessage]); // Store the formatted message
          // console.log("📝 Combined Message:\n", fullMessage);
        }
    
        setProcessing(false); // Processing complete
        messageBuffer.current = ""; // Clear buffer after successful processing
      } catch (e) {
        if (e instanceof SyntaxError) {
          console.log("⚠️ Received incomplete JSON, waiting for more data...");
        } else {
          console.error("❌ Error processing message: ", e);
          messageBuffer.current = ""; // Clear buffer if error is not related to JSON parsing
        }
      }
    };    

    ws.current.onerror = (error) => {
      console.error("❌ WebSocket Error: ", error);
    };

    ws.current.onclose = (event) => {
      if (event.wasClean) {
        // console.log(`ℹ️ WebSocket closed cleanly, code=${event.code}, reason=${event.reason}`);
      } else {
        console.log("⚠️ WebSocket Disconnected unexpectedly");
      }
    };

    return () => {
      if (ws.current) {
        ws.current.close();
      }
    };
  }, [initialMessage, setProcessing]);

  return (
    <Grid container direction="row" justifyContent="flex-start" alignItems="flex-end">
      <Grid item>
        <Avatar alt="Bot Avatar" src={botAvatar} />
      </Grid>
      {ALLOW_MARKDOWN_BOT ? (
        <Grid item className="botMessage" sx={{ backgroundColor: (theme) => theme.palette.background.botMessage }}>
          <ReactMarkdown>{responses.join("\n")}</ReactMarkdown>
        </Grid>
      ) : (
        <Grid item className="botMessage" sx={{ backgroundColor: (theme) => theme.palette.background.botMessage }}>
          <Typography variant="body2">{responses.join("\n")}</Typography>
        </Grid>
      )}
    </Grid>
  );
};

export default StreamingMessage;
