// --------------------------------------------------------------------------------------------------------//
// Primary color constants for the theme
export const PRIMARY_MAIN = "#1F1463"; // The main primary color used for buttons, highlights, etc.
export const primary_50 = "#5E97FF33"; // The 50 variant of the primary color

// Background color constants
export const SECONDARY_MAIN = "#3724AD"; // The main secondary color used for less prominent elements

// Chat component background colors
export const CHAT_BODY_BACKGROUND = "#FFFFFF"; // Background color for the chat body area
export const CHAT_LEFT_PANEL_BACKGROUND = "#F5F8FECC"; // Background color for the left panel in the chat
export const ABOUT_US_HEADER_BACKGROUND = "#1F1463"; // Background color for the About Us section in the left panel
export const CONTACTS_BACKGROUND = "#1F1463"; // Background color for the Contact Us section in the left panel
export const FAQ_HEADER_BACKGROUND = "#1F1463"; // Background color for the FAQ section in the left panel
export const ABOUT_US_TEXT = "#000000"; // Text color for the About Us section in the left panel
export const CONTACTS_TEXT = "#000000"; // Text color for the Contact Us section in the left panel
export const FAQ_TEXT = "#000000"; // Text color for the FAQ section in the left panel
export const HEADER_BACKGROUND = "#3724AD"; // Background color for the header
export const HEADER_TEXT_GRADIENT = "#3724AD"; // Text gradient color for the header

// Message background colors
export const BOTMESSAGE_BACKGROUND = "#F9F8FF"; // Background color for messages sent by the bot
export const USERMESSAGE_BACKGROUND = "#F9F9F9"; // Background color for messages sent by the user

// --------------------------------------------------------------------------------------------------------//
// --------------------------------------------------------------------------------------------------------//

// Text Constants
// Text Constants
export const TEXT = {
  EN: {
    APP_NAME: "Chatbot Template App",
    APP_ASSISTANT_NAME: "GenAI Bot",
    ABOUT_US_TITLE: "About us",
    ABOUT_US: "This virtual assistant helps families in Brightpoint’s Doula and Home Visiting programs access essential services, providing referrals and next steps to ensure they get the support they need.",
    CONTACT_US_TITLE: "If this is an emergency, contact:",
    CONTACT_US: [
      ["Emergency Services", "911"],
      ["CARES", "800-345-9049"],
      ["SASS", "773-523-4504"],
      ["Crisis Counselor", "988"],
    ],
    FAQ_TITLE: "Frequently Asked Questions",
    FAQS: [
      "Where can I find affordable childcare near me?",
      "How do I apply for food assistance?",
      "Are there any housing support programs in my area?",
      "Where can I find family planning near me?",
      "How do I access mental health services for my family?",
      "Where can I find financial assistance for utility bills?",
    ],
    CHAT_HEADER_TITLE: "Service Referral Agent",
    CHAT_INPUT_PLACEHOLDER: "Type a Query...",
    HELPER_TEXT: "Cannot send empty message",
    SPEECH_RECOGNITION_START: "Start Listening",
    SPEECH_RECOGNITION_STOP: "Stop Listening",
    SPEECH_RECOGNITION_HELPER_TEXT: "Stop speaking to send the message"
  },
  ES: {
    APP_NAME: "Aplicación de Plantilla de Chatbot",
    APP_ASSISTANT_NAME: "Bot GenAI",
    ABOUT_US_TITLE: "Sobre nosotros",
    ABOUT_US: "Este asistente virtual ayuda a las familias en los programas de Doula y Visitas Domiciliarias de Brightpoint a acceder a servicios esenciales, brindándoles referencias y próximos pasos para garantizar que reciban el apoyo que necesitan.",
    CONTACT_US_TITLE: "Si se trata de una emergencia, contacta:",
    CONTACT_US: [
      ["Servicios de emergencia", "911"],
      ["CARES", "800-345-9049"],
      ["SASS", "773-523-4504"],
      ["Consejero de crisis", "988"],
    ],
    FAQ_TITLE: "Preguntas Frecuentes",
    FAQS: [
      "¿Dónde puedo encontrar cuidado infantil asequible cerca de mí?",
      "¿Cómo solicito asistencia alimentaria?",
      "¿Existen programas de apoyo de vivienda en mi zona?",
      "¿Dónde puedo encontrar planificación familiar cerca de mí?",
      "¿Cómo puedo acceder a servicios de salud mental para mi familia?",
      "¿Dónde puedo encontrar ayuda financiera para las facturas de servicios públicos?",
    ],
    CHAT_HEADER_TITLE: "Agente de Referencia de Servicios",
    CHAT_INPUT_PLACEHOLDER: "Escribe una consulta...",
    HELPER_TEXT: "No se puede enviar un mensaje vacío",
    SPEECH_RECOGNITION_START: "Comenzar a escuchar",
    SPEECH_RECOGNITION_STOP: "Dejar de escuchar",
    SPEECH_RECOGNITION_HELPER_TEXT: "Deja de hablar para enviar el mensaje"
  },
  PL: {
    APP_NAME: "Aplikacja Szablonu Chatbota",
    APP_ASSISTANT_NAME: "Bot GenAI",
    ABOUT_US_TITLE: "O nas",
    ABOUT_US: "Ten wirtualny asystent pomaga rodzinom w programach Doula i Wizyt Domowych Brightpoint uzyskać dostęp do podstawowych usług, zapewniając skierowania i kolejne kroki, aby zapewnić potrzebne wsparcie.",
    CONTACT_US_TITLE: "W nagłych przypadkach skontaktuj się z:",
    CONTACT_US: [
      ["Służby ratunkowe", "911"],
      ["CARES", "800-345-9049"],
      ["SASS", "773-523-4504"],
      ["Konsultant kryzysowy", "988"],
    ],
    FAQ_TITLE: "Często Zadawane Pytania",
    FAQS: [
      "Gdzie mogę znaleźć niedrogą opiekę nad dziećmi w mojej okolicy?",
      "Jak mogę ubiegać się o pomoc żywnościową?",
      "Czy w mojej okolicy są dostępne programy wsparcia mieszkaniowego?",
      "Gdzie mogę znaleźć planowanie rodziny w pobliżu?",
      "Jak mogę uzyskać dostęp do usług zdrowia psychicznego dla mojej rodziny?",
      "Gdzie mogę uzyskać pomoc finansową na opłacenie rachunków za media?",
    ],
    CHAT_HEADER_TITLE: "Agent Skierowań do Usług",
    CHAT_INPUT_PLACEHOLDER: "Wpisz zapytanie...",
    HELPER_TEXT: "Nie można wysłać pustej wiadomości",
    SPEECH_RECOGNITION_START: "Rozpocznij nasłuchiwanie",
    SPEECH_RECOGNITION_STOP: "Zatrzymaj nasłuchiwanie",
    SPEECH_RECOGNITION_HELPER_TEXT: "Przestań mówić, aby wysłać wiadomość"
  },
};

export const SWITCH_TEXT = {
  SWITCH_LANGUAGE_ENGLISH: "English",
  SWITCH_TOOLTIP_ENGLISH: "Language",
  SWITCH_LANGUAGE_SPANISH: "Español",
  SWITCH_TOOLTIP_SPANISH: "Idioma",
};

export const LANDING_PAGE_TEXT = {
  EN: {
    CHOOSE_LANGUAGE: "Choose language:",
    ENGLISH: "English",
    SPANISH: "Español",
    SAVE_CONTINUE: "Save and Continue",
    APP_ASSISTANT_NAME: "Sample GenAI Bot Landing Page",
  },
  ES: {
    CHOOSE_LANGUAGE: "Elige el idioma:",
    ENGLISH: "Inglés",
    SPANISH: "Español",
    SAVE_CONTINUE: "Guardar y continuar",
    APP_ASSISTANT_NAME: "Página de inicio del Bot GenAI de ejemplo",
  },
  PL: {
    CHOOSE_LANGUAGE: "Wybierz język:",
    ENGLISH: "Angielski",
    SPANISH: "Hiszpański",
    SAVE_CONTINUE: "Zapisz i kontynuuj",
    APP_ASSISTANT_NAME: "Przykładowa strona powitalna Bota GenAI",
  }
};


// --------------------------------------------------------------------------------------------------------//
// --------------------------------------------------------------------------------------------------------//

// API endpoints
// WebSocket APIs
export const CHAT_API = process.env.REACT_APP_CHAT_API;
export const USER_API = process.env.REACT_APP_USER_API;
export const REFERRAL_MANAGEMENT_API = process.env.REACT_APP_REFERRAL_MANAGEMENT_API;

// REST APIs
export const ANALYTICS_API = process.env.REACT_APP_ANALYTICS_API;
export const USER_ADD_API = process.env.REACT_APP_USER_ADD_API;

export const REFERRAL_CHATBOT_REST_API = process.env.REACT_APP_REFERRAL_CHATBOT_REST_API;
export const REFERRALS_REST_API = process.env.REACT_APP_REFERRALS_REST_API;

console.log("API Configuration from CDK:");
console.log("CHAT_API:", CHAT_API);
console.log("USER_API:", USER_API);
console.log("REFERRAL_MANAGEMENT_API:", REFERRAL_MANAGEMENT_API);
console.log("ANALYTICS_API:", ANALYTICS_API);
console.log("USER_ADD_API:", USER_ADD_API);

// ✅ Environment info
export const ENVIRONMENT = process.env.REACT_APP_ENVIRONMENT || 'dev';
export const AWS_REGION = process.env.REACT_APP_REGION || 'us-east-1';

// ✅ Validation check
const requiredEnvVars = [
    'REACT_APP_CHAT_API',
    'REACT_APP_USER_API',
    'REACT_APP_REFERRAL_MANAGEMENT_API',
    'REACT_APP_ANALYTICS_API',
    'REACT_APP_USER_ADD_API'
];

const missingVars = requiredEnvVars.filter(envVar => !process.env[envVar]);
if (missingVars.length > 0) {
    console.warn("Missing environment variables (using fallbacks):", missingVars);
    console.warn("Make sure your CDK deployment set these in Amplify environment variables");
}
// --------------------------------------------------------------------------------------------------------//

// Features
export const ALLOW_FILE_UPLOAD = false; // Set to true to enable file upload feature
export const ALLOW_VOICE_RECOGNITION = true; // Set to true to enable voice recognition feature

export const ALLOW_MULTLINGUAL_TOGGLE = true; // Set to true to enable multilingual support
export const ALLOW_LANDING_PAGE = true; // Set to true to enable the landing page

// --------------------------------------------------------------------------------------------------------//
// Styling under work, would reccomend keeping it false for now
export const ALLOW_MARKDOWN_BOT = false; // Set to true to enable markdown support for bot messages
export const ALLOW_FAQ = true; // Set to true to enable the FAQs to be visible in Chat body 
