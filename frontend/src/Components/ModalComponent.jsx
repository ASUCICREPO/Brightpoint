import React from "react";
import { Box, Button, Typography } from "@mui/material";
import ModalImage from "../Assets/modal1.svg";

const ModalComponent = ({ openModal, setOpenModal, referralQuestions }) => {
  if (!openModal || !referralQuestions?.length) return null;

  const handleClose = () => {
    setTimeout(() => {
      setOpenModal(false);
    }, 100);
  };

  const handleAnswer = (referralId, answer) => {
    console.log(`Referral ID: ${referralId}, Answer: ${answer}`);
    // API call logic here
  };

  return (
    <Box
      sx={{
        position: "fixed",
        top: "50%",
        left: "50%",
        transform: "translate(-50%, -50%)",
        width: "60%",
        maxHeight: "50vh",
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
        <Typography variant="h6" sx={{ marginBottom: 2 }}>
          Hi there, did the following referrals help you with your queries? Please reply with yes or no:
        </Typography>

        {referralQuestions.map((q) => (
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
