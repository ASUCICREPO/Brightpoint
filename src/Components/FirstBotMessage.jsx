// FirstBotMessage.js
import React from 'react';
import { Typography, Grid, Box } from '@mui/material';
import PhoneIcon from "../Assets/phone_icon.svg"

const FirstBotMessage = ({ language }) => {
  const translations = {
    en: {
      text: "Welcome to the Service Referral Agent. If this is an emergency, please contact the services listed below. Feel free to ask the bot questions about any referrals you need help with!",
      title: "Medical & Mental Health Emergency Contacts:",
      police: "Emergency Services",
      policePhone: "911",
      policeInfo: "If immediate assistance is required or there is a medical or mental health emergency.",
      cares: "CARES",
      caresPhone: "800-345-9049",
      caresInfo: "The CARES Hotline is available 24/7, 365 days a year to both Medicaid and non-Medicaid individuals. A CARES Line worker will discuss the crisis with you and determine eligibility for a Mobile Crisis Response. If eligible, CARES will dispatch a responder within 2 hours.",
      sass: "SASS",
      sassPhone: "773-523-4504",
      sassInfo: "The Screening, Assessment, and Support Services (SASS) program is for individuals under the age of 21 experiencing a mental health crisis. CARES will determine eligibility for crisis services.",
      crisisCounselor: "Crisis Counselor",
      crisisPhone: "988",
      crisisInfo: "If someone is in crisis and needs someone to talk to, they can call or text 988. A trained crisis counselor will assist. This lifeline is confidential and available 24/7.",
      activeLabor: "Active Labor",
      activeLaborInfo: "If you are in active labor, go to your local Emergency Room and call your doula.",
    },
    es: {
      text: "Bienvenido al Agente de Referencias de Servicios. Si se trata de una emergencia, comuníquese con los servicios que se indican a continuación. ¡No dude en preguntarle al bot sobre cualquier referencia con la que necesite ayuda!",
      title: "Contactos de Emergencia Médica y de Salud Mental:",
      police: "Servicios de Emergencia",
      policePhone: "911",
      policeInfo: "Si se necesita asistencia inmediata o hay una emergencia médica o de salud mental.",
      cares: "CARES",
      caresPhone: "800-345-9049",
      caresInfo: "La línea de atención de CARES está disponible las 24 horas, los 365 días del año para personas con y sin Medicaid. Un trabajador hablará contigo sobre la crisis y determinará si se necesita una respuesta inmediata de crisis móvil. Si es elegible, enviarán a un trabajador en menos de 2 horas.",
      sass: "SASS",
      sassPhone: "773-523-4504",
      sassInfo: "El programa de Evaluación y Apoyo (SASS) es para personas menores de 21 años que enfrentan una crisis de salud mental. CARES evaluará la elegibilidad para servicios de crisis.",
      crisisCounselor: "Consejero de Crisis",
      crisisPhone: "988",
      crisisInfo: "Si alguien está en crisis y necesita hablar con alguien, puede llamar o enviar un mensaje de texto al 988. Un consejero capacitado responderá. Es confidencial y disponible las 24 horas.",
      activeLabor: "Trabajo de Parto Activo",
      activeLaborInfo: "Si estás en trabajo de parto activo, acude a la sala de emergencias más cercana y llama a tu doula.",
    },
    pl: {
      text: "Witamy w Agencie Skierowań do Usług. W nagłych przypadkach skontaktuj się z poniższymi służbami. Śmiało zadawaj botowi pytania dotyczące potrzebnych skierowań!",
      title: "Kontakty alarmowe: medyczne i zdrowia psychicznego:",
      police: "Służby ratunkowe",
      policePhone: "911",
      policeInfo: "W przypadku potrzeby natychmiastowej pomocy lub nagłego zagrożenia zdrowia fizycznego lub psychicznego.",
      cares: "CARES",
      caresPhone: "800-345-9049",
      caresInfo: "Infolinia CARES działa 24/7 przez cały rok i jest dostępna dla osób z Medicaid i bez. Pracownik CARES omówi sytuację kryzysową i określi, czy potrzebna jest mobilna odpowiedź kryzysowa. W razie potrzeby pracownik zostanie wysłany w ciągu 2 godzin.",
      sass: "SASS",
      sassPhone: "773-523-4504",
      sassInfo: "Program SASS (Ocena i Wsparcie Kryzysowe) jest przeznaczony dla osób poniżej 21 roku życia doświadczających kryzysu zdrowia psychicznego. CARES oceni kwalifikacje do usług kryzysowych.",
      crisisCounselor: "Doradca Kryzysowy",
      crisisPhone: "988",
      crisisInfo: "Jeśli ktoś przechodzi kryzys i potrzebuje rozmowy, może zadzwonić lub wysłać SMS na 988. Doradca kryzysowy pomoże przejść przez sytuację. Linia jest poufna i dostępna całą dobę.",
      activeLabor: "Poród aktywny",
      activeLaborInfo: "Jeśli jesteś w aktywnym porodzie, udaj się do najbliższego szpitala i zadzwoń do swojej douli.",
    }
  };
  

  const messages = translations[language] || translations.en;

  return (
    <Box sx={{ width: '100%' }}>
      <Typography
        variant="h5"
        sx={{
          color: (theme) => theme.palette.primary.main,
          fontWeight: 'bold',
          textAlign: 'left',
        }}
      >
        {messages.text}
      </Typography>
      <Typography
        variant="h5"
        sx={{
          color: (theme) => theme.palette.primary.main,
          fontWeight: 'bold',
          textAlign: 'left',
        }}
      >
        {messages.title}
      </Typography>

      {/* Emergency Contact Table */}
      <Grid item xs={12}>
        <Box sx={{
          display: 'table',
          width: '100%',
          borderCollapse: 'collapse',
        }}>
          {/* Row 1 */}
          <Box
            sx={{
              display: 'flex',
              borderBottom: '1px solid rgba(0, 0, 0, 0.1)',
              padding: '8px 0',
            }}
          >
            <Box sx={{ width: '30%', paddingLeft: 1 }}>
            <Typography variant="h6" sx={{ fontWeight: 'bold' }}>
                {messages.police}
              </Typography>
              <Box display="flex" alignItems="center">
                <img src={PhoneIcon} alt="Phone Icon" style={{ width: 20, height: 20, marginRight: 8 }} />
                <Typography variant=" h6" sx={{ fontWeight: 'bold' }}>
                  {messages.policePhone}
                </Typography>
              </Box>
            </Box>
            <Box sx={{ width: '70%' }}>
              <Typography variant=" h6">
                {messages.policeInfo}
              </Typography>
            </Box>
          </Box>
          {/* Row 2 */}
          <Box
            sx={{
              display: 'flex',
              borderBottom: '1px solid rgba(0, 0, 0, 0.1)',
              padding: '8px 0',
            }}
          >
            <Box sx={{ width: '30%', paddingLeft: 1 }}>
            <Typography variant="h6" sx={{ fontWeight: 'bold' }}>
                {messages.cares}
              </Typography>
              <Box display="flex" alignItems="center">
                <img src={PhoneIcon} alt="Phone Icon" style={{ width: 20, height: 20, marginRight: 8 }} />
                <Typography variant=" h6" sx={{ fontWeight: 'bold' }}>
                {messages.caresPhone}
                </Typography>
              </Box>
            </Box>
            <Box sx={{ width: '70%' }}>
              <Typography variant=" h6">
                {messages.caresInfo}
              </Typography>
            </Box>
          </Box>
          {/* Row 3 */}
          <Box
            sx={{
              display: 'flex',
              borderBottom: '1px solid rgba(0, 0, 0, 0.1)',
              padding: '8px 0',
            }}
          >
            <Box sx={{ width: '30%', paddingLeft: 1 }}>
            <Typography variant="h6" sx={{ fontWeight: 'bold' }}>
                {messages.sass}
              </Typography>
              <Box display="flex" alignItems="center">
                <img src={PhoneIcon} alt="Phone Icon" style={{ width: 20, height: 20, marginRight: 8 }} />
                <Typography variant=" h6" sx={{ fontWeight: 'bold' }}>
                {messages.sassPhone}
                </Typography>
              </Box>
            </Box>
            <Box sx={{ width: '70%' }}>
              <Typography variant=" h6">
                {messages.sassInfo}
              </Typography>
            </Box>
          </Box>
          {/* Row 4 */}
          <Box
            sx={{
              display: 'flex',
              borderBottom: '1px solid rgba(0, 0, 0, 0.1)',
              padding: '8px 0',
            }}
          >
            <Box sx={{ width: '30%', paddingLeft: 1 }}>
            <Typography variant="h6" sx={{ fontWeight: 'bold' }}>
                {messages.crisisCounselor}
              </Typography>
              <Box display="flex" alignItems="center">
                <img src={PhoneIcon} alt="Phone Icon" style={{ width: 20, height: 20, marginRight: 8 }} />
                <Typography variant=" h6" sx={{ fontWeight: 'bold' }}>
                  {messages.crisisPhone}
                </Typography>
              </Box>
            </Box>
            <Box sx={{ width: '70%' }}>
              <Typography variant=" h6">
                {messages.crisisInfo}
              </Typography>
            </Box>
          </Box>
          {/* Row 5 */}
          <Box
            sx={{
              display: 'flex',
              padding: '8px 0',
            }}
          >
            <Box sx={{ width: '30%', paddingLeft: 1 }}>
            <Typography variant="h6" sx={{ fontWeight: 'bold' }}>
                {messages.activeLabor}
              </Typography>
            </Box>
            <Box sx={{ width: '70%' }}>
              <Typography variant=" h6">
                {messages.activeLaborInfo}
              </Typography>
            </Box>
          </Box>
        </Box>
      </Grid>
    </Box>
  );
};

export default FirstBotMessage;
