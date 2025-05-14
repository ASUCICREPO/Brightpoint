import React, { useState } from "react";
import Grid from "@mui/material/Grid";
import Typography from "@mui/material/Typography";
import Divider from "@mui/material/Divider";
import IconButton from "@mui/material/IconButton";
import useMediaQuery from "@mui/material/useMediaQuery";
import { useTheme } from "@mui/material/styles";
import ExpandMoreIcon from "@mui/icons-material/ExpandMore";
import ExpandLessIcon from "@mui/icons-material/ExpandLess";
import { useLocation } from "react-router-dom";

import {
  ABOUT_US_HEADER_BACKGROUND,
  ABOUT_US_TEXT,
  CONTACTS_BACKGROUND,
  CONTACTS_TEXT,
  FAQ_HEADER_BACKGROUND,
  TEXT,
} from "../utilities/constants";
import phoneIcon from "../Assets/phone_icon.svg";

function LeftNav({ showLeftNav = true }) {
  const location = useLocation();
  const path = location.pathname;

  let language = "EN";
  if (path.startsWith("/esapp")) language = "ES";
  else if (path.startsWith("/plapp")) language = "PL";

  const theme = useTheme();
  const isSmallScreen = useMediaQuery(theme.breakpoints.down("sm"));
  const [isCollapsed, setIsCollapsed] = useState(isSmallScreen);

  const toggleCollapse = () => {
    setIsCollapsed(!isCollapsed);
  };

  return (
    <Grid className="appHeight100" sx={{ width: isCollapsed ? "auto" : "100%", position: "relative" }}>
      <Grid container direction="column" justifyContent="flex-start" alignItems="stretch" padding={4} spacing={2}>
        {/* Collapse Toggle for small screens */}
        {isSmallScreen && (
          <Grid item sx={{ position: "absolute", top: 10, right: 10, zIndex: 1 }}>
            <IconButton onClick={toggleCollapse} size="small">
              {isCollapsed ? <ExpandMoreIcon /> : <ExpandLessIcon />}
            </IconButton>
          </Grid>
        )}

        {!isCollapsed && showLeftNav && (
          <>
            {/* About Us */}
            <Grid item>
              <Typography
                variant="h6"
                sx={{
                  fontWeight: "bold",
                  fontSize: { xs: "1rem", sm: "1.25rem" },
                }}
                color={ABOUT_US_HEADER_BACKGROUND}
              >
                {TEXT[language].ABOUT_US_TITLE}
              </Typography>
            </Grid>
            <Grid item>
              <Typography
                variant="subtitle1"
                sx={{ px: 2, fontSize: { xs: "0.875rem", sm: "1rem" } }}
                color={ABOUT_US_TEXT}
              >
                {TEXT[language].ABOUT_US}
              </Typography>
            </Grid>

            {/* Contact Section */}
            <Grid item>
              <Typography
                variant="h6"
                sx={{
                  fontWeight: "bold",
                  fontSize: { xs: "1rem", sm: "1.25rem" },
                }}
                color={CONTACTS_BACKGROUND}
              >
                {TEXT[language].CONTACT_US_TITLE}
              </Typography>
            </Grid>

            {TEXT[language].CONTACT_US.map(([name, phone], index) => (
              <React.Fragment key={index}>
                <Grid container alignItems="center" justifyContent="space-between" sx={{ px: 4 }}>
                  <Grid item xs={6}>
                    <Typography
                      variant="subtitle1"
                      sx={{ fontSize: { xs: "0.875rem", sm: "1rem" } }}
                      color={CONTACTS_TEXT}
                    >
                      {name}
                    </Typography>
                  </Grid>
                  <Grid item container xs={6} justifyContent="flex-end" alignItems="center" spacing={1}>
                    <Grid item>
                      <img src={phoneIcon} alt="Phone Icon" width={16} height={16} />
                    </Grid>
                    <Grid item>
                      <Typography
                        variant="subtitle1"
                        sx={{ fontSize: { xs: "0.875rem", sm: "1rem" } }}
                        color={CONTACTS_TEXT}
                      >
                        {phone}
                      </Typography>
                    </Grid>
                  </Grid>
                </Grid>
                {index < TEXT[language].CONTACT_US.length - 1 && (
                  <Divider sx={{ backgroundColor: "#d3d3d3", margin: "0" }} />
                )}
              </React.Fragment>
            ))}

            {/* FAQ Section */}
            <Grid item sx={{ marginTop: 2 }}>
              <Typography
                variant="h6"
                sx={{
                  fontWeight: "bold",
                  fontSize: { xs: "1rem", sm: "1.25rem" },
                }}
                color={FAQ_HEADER_BACKGROUND}
              >
                {TEXT[language].FAQ_TITLE}
              </Typography>
            </Grid>
            <ul style={{ listStyleType: "disc", paddingLeft: "20px", marginTop: 0 }}>
              {TEXT[language].FAQS.map((question, index) => (
                <li key={index} style={{ color: "black", paddingLeft: "8px" }}>
                  <Typography variant="subtitle1" sx={{ fontSize: { xs: "0.875rem", sm: "1rem" } }}>
                    {question}
                  </Typography>
                </li>
              ))}
            </ul>
          </>
        )}
      </Grid>
    </Grid>
  );
}

export default LeftNav;
