import React from "react";
import { Box, Button, Typography } from "@mui/material";
import ModalImage from "../Assets/modal1.svg";

const ModalComponent = ({ openModal, setOpenModal }) => {
  if (!openModal) return null; // Render only when open

  const handleClose = () => {
    setTimeout(() => {
      setOpenModal(false);
    }, 100);
  };

  const handleAnswer = (referralId, answer) => {
    console.log(`Referral ID: ${referralId}, Answer: ${answer}`);
    // Here you can make an API call to submit the answer
  };

  // Hardcoded feedback data based on your structure
  const feedbackQuestions = [
    {
      referral_id: '01c79ad5-0378-4148-968a-c556ba797d94',
      agency: "East Peoria Food Pantry – First United Methodist Church of Peoria",
      question: "Hi test, Did the referral East Peoria Food Pantry – First United Methodist Church of Peoria, 154 E Washington St, East Peoria, 61611, 61611 help you in Food Assistance? Please reply with yes or no.",
      service_category: "Food Assistance"
    },
    {
      referral_id: '030536cb-4039-429b-88a2-42e638aa7524',
      agency: "Pekin Township Food Pantry",
      question: "Hi test, Did the referral Pekin Township Food Pantry, 420 Elizabeth St, Pekin, Not specified help you in Food Assistance? Please reply with yes or no.",
      service_category: "Food Assistance"
    },
    {
      referral_id: '0ac1a663-8923-476a-b86d-73be1b695539',
      agency: "PATH 24/7 Crisis and Referral Hotline",
      question: "Hi test, Did the referral PATH 24/7 Crisis and Referral Hotline, 500 E. Monroe St, 62701 help you in Services for Seniors & Individuals with Disabilities? Please reply with yes or no.",
      service_category: "Services for Seniors & Individuals with Disabilities"
    },
    {
      referral_id: '1efa8cb0-e227-41ed-97b3-2a5121dbc35c',
      agency: "Child Abuse Hotline",
      question: "Hi test, Did the referral Child Abuse Hotline, 406 E. Monroe St., 62701 help you in Children Services? Please reply with yes or no.",
      service_category: "Children Services"
    },
    {
      referral_id: '2e51bf33-aeed-4147-a07a-2f9276bcdffa',
      agency: "PATH 24/7 Crisis and Referral Hotline",
      question: "Hi test, Did the referral PATH 24/7 Crisis and Referral Hotline, 1-800-621-4000, 62701 help you in Food Pantry Referrals? Please reply with yes or no.",
      service_category: "Food Pantry Referrals"
    }
  ];

  return (
    <Box
      sx={{
        position: "fixed",
        top: "50%",
        left: "50%",
        transform: "translate(-50%, -50%)",
        width: "60%",
        maxHeight: "80vh",
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
      {/* Left side - Image */}
      <Box
        sx={{
          width: "35%",
          backgroundColor: "#E5E1FF",
          display: "flex",
          justifyContent: "center",
          alignItems: "center",
          borderRadius: "20px 0 0 20px",
        }}
      >
        <img src={ModalImage} alt="Modal" style={{ width: "80%" }} />
      </Box>

      {/* Right side - Questions */}
      <Box sx={{ width: "65%", paddingLeft: 3 }}>
        <Typography variant="h4" sx={{ fontWeight: "bold", marginBottom: 2 }}>
          Welcome Back!
        </Typography>
        <Typography variant="h6" sx={{ marginBottom: 2 }}>
          Hi test, did the following referrals help you with your queries? Please reply with yes or no:
        </Typography>

        {feedbackQuestions.length > 0 ? (
          feedbackQuestions.map((q, index) => (
            <Box key={q.referral_id} sx={{ marginBottom: 4 }}>
              <Typography variant="body1" sx={{ fontWeight: "medium", marginBottom: 1 }}>
                <strong>{q.agency}</strong> in {q.service_category}
              </Typography>
              <Button
                variant="outlined"
                sx={{ borderRadius: "20px", marginRight: 2 }}
                onClick={() => handleAnswer(q.referral_id, "Yes")}
              >
                Yes
              </Button>
              <Button
                variant="outlined"
                sx={{ borderRadius: "20px" }}
                onClick={() => handleAnswer(q.referral_id, "No")}
              >
                No
              </Button>
            </Box>
          ))
        ) : (
          <Typography>No referral questions available.</Typography>
        )}

        {/* Close Modal button at bottom */}
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
