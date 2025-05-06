import React, { createContext, useState, useContext, useEffect } from "react";

const UserContext = createContext();

export const UserProvider = ({ children }) => {
  const [userData, setUserData] = useState({
    user_id: '',
    username: '',
    email: '',
    zipcode: '',
    phoneNumber: '',
    language: '',
    referrals: [],
    feedbackQuestions: [],
  });

  const updateUser = (newData) => {
    setUserData((prev) => ({ ...prev, ...newData }));
  };

  useEffect(() => {
    console.log("Updated User Context:", userData);
  }, [userData]);

  return (
    <UserContext.Provider value={{ userData, updateUser }}>
      {children}
    </UserContext.Provider>
  );
};

export const useUser = () => useContext(UserContext);
