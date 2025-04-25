// FirstBotMessage.js
import React from 'react';
import { Typography, Grid, Box } from '@mui/material';
import PhoneIcon from "../Assets/phone_icon.svg"

const FirstBotMessage = ({ language }) => {
  const translations = {
    en: {
      text: "Welcome to the Service Referral Agent, if this is an emergency please contact the services listed below. Feel free to ask the bot questions about any referrals you need help with!",
      title: "Medical & Mental Health Emergency Contacts:",
      police: "Emergency Services",
      policePhone: "911",
      policeInfo: "If immediate assistance is required or there is a medical or mental health emergency.",
      cares: "CARES",
      caresPhone: "800-345-9049",
      caresInfo: "The CARES Hotline is available 24/7, 365 days a year to both Medicaid and non-Medicaid individuals. A CARES Line worker will discuss the crisis with you, and the eligibility of the person in crisis to determine if immediate Mobile Crisis Response is needed. If eligible, CARES will send a Mobile Crisis Response worker who will respond to the place of the person in crisis within 2 hours.",
      sass: "SASS",
      sassPhone: "773-523-4504",
      sassInfo: "The Screening Assessment and Support Services (SASS) program is for individuals under the age of 21 who are experiencing a mental health crisis. CARES will determine SASS eligibility for crisis services.",
      crisisCounselor: "Crisis Counselor",
      crisisPhone: "988",
      crisisInfo: "If someone is experiencing a crisis and wants someone to talk to, they can call or text 988 or you can call or text for them. A trained crisis counselor will talk or text with you to navigate the crisis. 988 is a confidential lifeline and available 24/7.",
      activeLabor: "Active Labor",
      activeLaborInfo: "If you are in active labor, go to your local Emergency Room and call your doula.",
    },
    es: {
      text: "Bienvenido al Agente de Referencias de Servicios. Si se trata de una emergencia, comuníquese con los servicios que se indican a continuación. ¡No dude en preguntarle al bot sobre cualquier referencia con la que necesite ayuda!",
      title: "Contactos de Emergencia Médica y de Salud Mental:",
      police: "Policía",
      policePhone: "911",
      policeInfo: "Si se necesita asistencia inmediata o hay una emergencia médica o de salud mental.",
      cares: "CARES",
      caresPhone: "800-345-9049",
      caresInfo: "La línea de atención de CARES está disponible las 24 horas, los 365 días del año para individuos con y sin Medicaid. Un trabajador de la línea CARES discutirá la crisis contigo y determinará la elegibilidad de la persona en crisis para determinar si se necesita una respuesta inmediata de Crisis Móvil. Si es elegible, CARES enviará un trabajador de Crisis Móvil que responderá al lugar de la persona en crisis en un plazo de 2 horas.",
      sass: "SASS",
      sassPhone: "773-523-4504",
      sassInfo: "El programa de Servicios de Evaluación y Apoyo (SASS) está dirigido a individuos menores de 21 años que están experimentando una crisis de salud mental. CARES determinará la elegibilidad de SASS para los servicios de crisis.",
      crisisCounselor: "Consejero de Crisis",
      crisisPhone: "988",
      crisisInfo: "Si alguien está experimentando una crisis y desea hablar con alguien, puede llamar o enviar un mensaje de texto al 988 o puedes llamar o enviar un mensaje de texto por ellos. Un consejero de crisis capacitado hablará o enviará un mensaje de texto contigo para navegar por la crisis. 988 es una línea confidencial y está disponible las 24 horas del día, los 7 días de la semana.",
      activeLabor: "Trabajo de Parto Activo",
      activeLaborInfo: "Si estás en trabajo de parto activo, ve a tu sala de emergencias local y llama a tu doula.",
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
