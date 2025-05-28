import React, { createContext, useContext, useState, useEffect } from 'react';
import { useCookies } from 'react-cookie';
import { ALLOW_LANDING_PAGE } from './constants'; // Set this to false if not using landing page

const LanguageContext = createContext();

export const LanguageProvider = ({ children }) => {
  const [cookies, setCookie] = useCookies(['language']);
  const supportedLanguages = ['EN', 'ES', 'PL'];
  const cookieLanguage = cookies.language;
  const defaultLanguage =
    supportedLanguages.includes(cookieLanguage)
      ? cookieLanguage
      : (!ALLOW_LANDING_PAGE ? 'EN' : '');

  const [language, setLanguage] = useState(defaultLanguage);

  useEffect(() => {
    if (language && cookies.language !== language) {
      setCookie('language', language, { path: '/' });
    }
  }, [language, setCookie, cookies.language]);

  return (
    <LanguageContext.Provider value={{ language, setLanguage }}>
      {children}
    </LanguageContext.Provider>
  );
};

export const useLanguage = () => {
  const context = useContext(LanguageContext);
  if (!context) {
    throw new Error('useLanguage must be used within a LanguageProvider');
  }
  return context;
};
