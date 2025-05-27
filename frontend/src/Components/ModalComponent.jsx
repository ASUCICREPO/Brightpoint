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
import { useUser } from "../utilities/UserContext";

const ModalComponent = ({ openModal, setOpenModal }) => {
  const { userData, updateUser } = useUser();

  // Get feedback questions from context
  const referralQuestions = userData?.feedbackQuestions || [];

  const [feedbackList, setFeedbackList] = useState([]);
  const [isLoading, setIsLoading] = useState(false);
  const [hasSubmittedFeedback, setHasSubmittedFeedback] = useState(false);
  const wsRef = useRef(null);

  // ✅ FIXED: Track if modal has been dismissed in this session
  const [modalDismissedThisSession, setModalDismissedThisSession] = useState(
    sessionStorage.getItem('feedbackModalDismissed') === 'true'
  );

  // ✅ FIXED: Track if auto-show has been attempted
  const [autoShowAttempted, setAutoShowAttempted] = useState(false);

  // ✅ FIXED: Effect to handle session-based modal showing (only once per session)
  useEffect(() => {
    // Only attempt auto-show once per component lifecycle and if not dismissed
    if (!autoShowAttempted &&
        !modalDismissedThisSession &&
        referralQuestions.length > 0 &&
        !openModal) {

      console.log("🎯 Auto-opening feedback modal for first time this session");
      setOpenModal(true);
      setAutoShowAttempted(true); // Mark that we've attempted auto-show
    }
  }, [referralQuestions, modalDismissedThisSession, openModal, setOpenModal, autoShowAttempted]);

  // Reset submission flag after a delay
  useEffect(() => {
    if (hasSubmittedFeedback) {
      const timer = setTimeout(() => {
        console.log("🔄 Resetting submission flag");
        setHasSubmittedFeedback(false);
      }, 3000);

      return () => clearTimeout(timer);
    }
  }, [hasSubmittedFeedback]);

  // Debug logging
  useEffect(() => {
    console.log("🔍 ModalComponent debug:", {
      openModal,
      questionsLength: referralQuestions.length,
      hasSubmittedFeedback,
      modalDismissedThisSession,
      autoShowAttempted,
      userDataExists: !!userData
    });
  }, [userData, openModal, hasSubmittedFeedback, modalDismissedThisSession, autoShowAttempted, referralQuestions]);

  // Initialize feedback list when modal opens
  useEffect(() => {
    console.log("📝 ModalComponent opened:", openModal);
    if (openModal && referralQuestions.length > 0) {
      const initialFeedback = referralQuestions.map((q) => ({
        referral_id: q.referral_id,
        feedback: "",
      }));
      setFeedbackList(initialFeedback);
      console.log("✅ Initialized feedback list:", initialFeedback);
    }
  }, [openModal, referralQuestions]);

  // WebSocket connection management
  useEffect(() => {
    if (openModal) {
      console.log("🔌 Opening WebSocket connection to:", USER_API);
      wsRef.current = new WebSocket(USER_API);

      wsRef.current.onopen = () => {
        console.log("✅ WebSocket opened successfully");
      };

      wsRef.current.onerror = (err) => {
        console.error("❌ WebSocket error:", err);
      };

      wsRef.current.onclose = (event) => {
        console.log("🔌 WebSocket closed:", event.code, event.reason);
      };

      wsRef.current.onmessage = (event) => {
        try {
          const response = JSON.parse(event.data);
          console.log("📩 Received feedback response:", response);

          // Update user context with new data after feedback submission
          if (response.user) {
            console.log("🔄 Updating user context after feedback submission");
            updateUser({
              ...response.user,
              feedbackQuestions: response.feedback_questions || []
            });
          }

          // Track successful feedback submission
          if (response.message && response.message.includes('Successfully recorded')) {
            console.log("✅ Feedback submission confirmed by backend");
            setHasSubmittedFeedback(true);
          }
        } catch (error) {
          console.error("❌ Error parsing WebSocket response:", error);
        }
      };
    }

    return () => {
      if (wsRef.current) {
        console.log("🔌 Closing WebSocket connection");
        wsRef.current.close();
      }
    };
  }, [openModal, updateUser]);

  const handleFeedbackChange = (referral_id, answer) => {
    console.log("📝 Feedback changed:", { referral_id, answer });
    setFeedbackList((prev) =>
      prev.map((item) =>
        item.referral_id === referral_id ? { ...item, feedback: answer } : item
      )
    );
  };

  const handleClose = async () => {
    setIsLoading(true);
    setHasSubmittedFeedback(true); // Mark as submitted immediately

    const userIdentifier = userData?.username || userData?.user_id || "unknown_user";

    const payload = {
      action: "sendFeedback",
      user_id: userIdentifier,
      Zipcode: userData?.zipcode || userData?.Zipcode || "",
      Phone: userData?.phoneNumber || userData?.Phone || "",
      Email: userData?.email || userData?.Email || "",
      language: userData?.language || "english",
      feedback_list: feedbackList,
    };

    console.log("📤 Sending feedback payload:", payload);

    if (wsRef.current?.readyState === WebSocket.OPEN) {
      wsRef.current.send(JSON.stringify(payload));
      console.log("✅ Feedback sent via WebSocket");
    } else {
      console.error("❌ WebSocket not open. State:", wsRef.current?.readyState);
    }

    // ✅ ADDED: Mark modal as dismissed after successful submission
    setModalDismissedThisSession(true);
    sessionStorage.setItem('feedbackModalDismissed', 'true');

    // Close modal
    setTimeout(() => {
      setOpenModal(false);
      setIsLoading(false);
      console.log("✅ Modal closed after feedback submission and marked as dismissed");
    }, 500);
  };

  // ✅ FIXED: Enhanced skip function that permanently dismisses modal for this session
  const handleSkip = () => {
    console.log("⏭️ User skipped feedback - permanently dismissing for this session");

    // Set loading state to prevent double-clicks
    setIsLoading(true);

    // ✅ IMPORTANT: Mark modal as dismissed for this session
    setModalDismissedThisSession(true);
    sessionStorage.setItem('feedbackModalDismissed', 'true');

    // Mark as submitted to prevent re-opening
    setHasSubmittedFeedback(true);

    // Close the modal immediately
    setOpenModal(false);

    // Reset loading state after a short delay
    setTimeout(() => {
      setIsLoading(false);
      console.log("✅ Skip completed, modal permanently dismissed for session");
    }, 100);
  };

  // ✅ UPDATED: Function to manually clear session storage (for testing/debugging)
  const clearSessionModalFlag = () => {
    sessionStorage.removeItem('feedbackModalDismissed');
    setModalDismissedThisSession(false);
    setAutoShowAttempted(false);
    console.log("🧹 Session modal flags cleared - modal can show again");
  };

  // ✅ ENHANCED: Better conditions for when to render modal
  if (!openModal || referralQuestions.length === 0) {
    console.log("🚫 Modal not rendering:", {
      openModal,
      questionsLength: referralQuestions.length
    });
    return null;
  }

  console.log("🎯 Rendering modal with", referralQuestions.length, "questions");

  return (
    <>
      {/* Backdrop */}
      <Box
        sx={{
          position: "fixed",
          top: 0,
          left: 0,
          width: "100vw",
          height: "100vh",
          backgroundColor: "rgba(0, 0, 0, 0.5)",
          zIndex: 1299,
        }}
        onClick={() => !isLoading && handleSkip()} // ✅ CHANGED: Use handleSkip instead of setOpenModal
      />

      {/* Modal Content */}
      <Box
        sx={{
          position: "fixed",
          top: "50%",
          left: "50%",
          transform: "translate(-50%, -50%)",
          width: { xs: "90%", sm: "80%", md: "60%", lg: "40%" },
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

          <Typography variant="body2" sx={{ marginBottom: 3, color: "gray" }}>
            We'd love to hear about your experience with these services:
          </Typography>

          {referralQuestions.map((q, index) => (
            <Box key={q.referral_id} sx={{ marginBottom: 2 }}>
              <Typography variant="body1" sx={{ marginBottom: 1, fontWeight: "500" }}>
                {q.question}
              </Typography>

              <Typography variant="caption" sx={{ marginBottom: 1, color: "gray", display: "block" }}>
                Service: {q.agency} | Category: {q.service_category}
                {q.source && ` | Source: ${q.source}`}
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
                <ToggleButton value="yes" sx={{ minWidth: "80px" }} disabled={isLoading}>
                  Yes
                </ToggleButton>
                <ToggleButton value="no" sx={{ minWidth: "80px" }} disabled={isLoading}>
                  No
                </ToggleButton>
              </ToggleButtonGroup>

              {index !== referralQuestions.length - 1 && <Divider sx={{ my: 2 }} />}
            </Box>
          ))}

          <Box sx={{ marginTop: 4, display: "flex", gap: 2 }}>
            <Button
              variant="contained"
              color="primary"
              sx={{ borderRadius: "20px", minWidth: "120px" }}
              onClick={handleClose}
              disabled={isLoading}
            >
              {isLoading ? "Sending..." : "Submit Feedback"}
            </Button>

            <Button
              variant="outlined"
              sx={{ borderRadius: "20px", minWidth: "80px" }}
              onClick={handleSkip}
              disabled={isLoading}
            >
              {isLoading ? "Closing..." : "Skip"}
            </Button>
          </Box>

          {/* ✅ NEW: Development helper to clear session flag */}
          {process.env.NODE_ENV === 'development' && (
            <Box sx={{ marginTop: 2 }}>
              <Button
                size="small"
                variant="text"
                onClick={clearSessionModalFlag}
                sx={{ fontSize: '10px', color: 'gray' }}
              >
                🧹 Clear Session Flag (Dev)
              </Button>
            </Box>
          )}
        </Box>
      </Box>
    </>
  );
};

export default ModalComponent;