import React, { useEffect, useState, useRef } from "react";
import {
  Box,
  Button,
  Typography,
  Divider,
  ToggleButton,
  ToggleButtonGroup,
} from "@mui/material";
import ModalImage from "../Assets/modal1.svg";
import { USER_API } from "../utilities/constants";
import { useUser } from "../utilities/UserContext"; // <-- Import context hook

const ModalComponent = ({ openModal, setOpenModal }) => {
  const { userData } = useUser(); // <-- Get userData from context
  const referralQuestions = userData.feedbackQuestions || [];

  const [feedbackList, setFeedbackList] = useState([]);
  const wsRef = useRef(null);

  useEffect(() => {
    console.log("ModalComponent opened:", openModal);
    if (openModal) {
      const initialFeedback = referralQuestions.map((q) => ({
        referral_id: q.referral_id,
        feedback: "",
      }));
      setFeedbackList(initialFeedback);
    }
  }, [openModal, referralQuestions]);

  useEffect(() => {
    if (openModal) {
      wsRef.current = new WebSocket(USER_API);
      wsRef.current.onopen = () => console.log("WebSocket opened");
      wsRef.current.onerror = (err) => console.error("WebSocket error:", err);
      wsRef.current.onclose = () => console.log("WebSocket closed");
    }
    return () => {
      if (wsRef.current) wsRef.current.close();
    };
  }, [openModal]);

  const handleFeedbackChange = (referral_id, answer) => {
    setFeedbackList((prev) =>
      prev.map((item) =>
        item.referral_id === referral_id ? { ...item, feedback: answer } : item
      )
    );
  };

  const handleClose = () => {
    const payload = {
      action: "sendFeedback",
      user_id: userData.user_id || "unknown_user",
      Zipcode: userData.zipcode || "",
      Phone: userData.phoneNumber || "",
      Email: userData.email || "",
      language: userData.language || "english",
      feedback_list: feedbackList,
    };

    console.log("Sending feedback payload:", payload);

    if (wsRef.current?.readyState === WebSocket.OPEN) {
      wsRef.current.send(JSON.stringify(payload));
    } else {
      console.error("WebSocket not open. Feedback not sent.");
    }

    setTimeout(() => setOpenModal(false), 100);
  };

  if (!openModal || referralQuestions.length === 0) return null;

  return (
    <Box
      sx={{
        position: "fixed",
        top: "50%",
        left: "50%",
        transform: "translate(-50%, -50%)",
        width: "40%",
        maxHeight: "70vh",
        overflowY: "auto",
        backgroundColor: "white",
        borderRadius: "20px",
        boxShadow: 24,
        padding: 4,
        display: "flex",
        flexDirection: "row",
        zIndex: 1300,
      }}
    >
      <Box
        sx={{
          width: "20%",
          backgroundColor: "#E5E1FF",
          display: "flex",
          justifyContent: "center",
          alignItems: "center",
          borderRadius: "20px 0 0 20px",
        }}
      >
        <img src={ModalImage} alt="Modal" style={{ width: "60%" }} />
      </Box>

      <Box sx={{ width: "80%", paddingLeft: 3 }}>
        <Typography variant="h4" sx={{ fontWeight: "bold", marginBottom: 2 }}>
          Welcome Back!
        </Typography>

        {referralQuestions.map((q, index) => (
          <Box key={q.referral_id} sx={{ marginBottom: 2 }}>
            <Typography variant="body1" sx={{ marginBottom: 1 }}>
              {q.question}
            </Typography>
            <ToggleButtonGroup
              color="primary"
              value={
                feedbackList.find((f) => f.referral_id === q.referral_id)
                  ?.feedback || ""
              }
              exclusive
              onChange={(e, newVal) =>
                newVal && handleFeedbackChange(q.referral_id, newVal)
              }
              sx={{ marginBottom: 2 }}
            >
              <ToggleButton value="yes">Yes</ToggleButton>
              <ToggleButton value="no">No</ToggleButton>
            </ToggleButtonGroup>
            {index !== referralQuestions.length - 1 && <Divider sx={{ my: 2 }} />}
          </Box>
        ))}

        <Box sx={{ marginTop: 4 }}>
          <Button
            variant="contained"
            color="primary"
            sx={{ borderRadius: "20px" }}
            onClick={handleClose}
          >
            Close
          </Button>
        </Box>
      </Box>
    </Box>
  );
};

export default ModalComponent;
