import React, { createContext, useState, useContext, useEffect } from "react";

// Create the UserContext
const UserContext = createContext();

// Provider Component
export const UserProvider = ({ children }) => {
    const [userData, setUserData] = useState({
      username: '',
  password: '',
  givenName: '',
  lastName: '',
  email: '',
  zipcode: '',
      referralId: null, // Store first referral ID
      referralQuestion: "", // Store first referral question
      feedbackQuestion: "" // Store the entire array

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
  

// Hook to use UserContext
export const useUser = () => useContext(UserContext);
