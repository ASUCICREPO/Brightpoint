import React from "react";
import Grid from "@mui/material/Grid";
import Typography from "@mui/material/Typography";
import Divider from "@mui/material/Divider";
import { useLanguage } from "../utilities/LanguageContext";
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
  const { language } = useLanguage(); // This will dynamically change

  return (
    <Grid className="appHeight100">
      <Grid container direction="column" justifyContent="flex-start" alignItems="stretch" padding={4} spacing={2}>
        {showLeftNav && (
          <>
            {/* About Us */}
            <Grid item>
              <Typography variant="h6" sx={{ fontWeight: "bold" }} color={ABOUT_US_HEADER_BACKGROUND}>
                {TEXT[language].ABOUT_US_TITLE}
              </Typography>
            </Grid>
            <Grid item>
              <Typography variant="subtitle1" sx={{ px: 2 }} color={ABOUT_US_TEXT}>
                {TEXT[language].ABOUT_US}
              </Typography>
            </Grid>

            {/* Contact Section */}
            <Grid item>
              <Typography variant="h6" sx={{ fontWeight: "bold" }} color={CONTACTS_BACKGROUND}>
                {TEXT[language].CONTACT_US_TITLE}
              </Typography>
            </Grid>

            {TEXT[language].CONTACT_US.map(([name, phone], index) => (
              <React.Fragment key={index}>
                <Grid container alignItems="center" justifyContent="space-between" sx={{ px: 4 }}>
                  <Grid item xs={6}>
                    <Typography variant="subtitle1" color={CONTACTS_TEXT}>
                      {name}
                    </Typography>
                  </Grid>
                  <Grid item container xs={6} justifyContent="flex-end" alignItems="center" spacing={1}>
                    <Grid item>
                      <img src={phoneIcon} alt="Phone Icon" width={16} height={16} />
                    </Grid>
                    <Grid item>
                      <Typography variant="subtitle1" color={CONTACTS_TEXT}>
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
              <Typography variant="h6" sx={{ fontWeight: "bold" }} color={FAQ_HEADER_BACKGROUND}>
                {TEXT[language].FAQ_TITLE}
              </Typography>
            </Grid>
            <ul style={{ listStyleType: "disc", paddingLeft: "20px", marginTop: 0 }}>
              {TEXT[language].FAQS.map((question, index) => (
                <li key={index} style={{ color: "black", paddingLeft: "8px" }}>
                  <Typography variant="subtitle1">{question}</Typography>
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
