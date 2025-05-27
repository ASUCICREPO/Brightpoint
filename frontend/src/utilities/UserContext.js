import React, { createContext, useState, useContext, useEffect } from "react";
import { USER_API } from "./constants"; // ✅ Add this import

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

  const [isLoading, setIsLoading] = useState(false); // ✅ Add loading state

  const updateUser = (newData) => {
    console.log("🔄 Updating user context with:", newData);
    setUserData((prev) => ({ ...prev, ...newData }));
  };

  // ✅ ADD: Function to fetch user data with feedback questions
  const fetchUserWithFeedback = async (userId, language = 'english') => {
    setIsLoading(true);
    console.log("📡 Fetching user data with feedback questions:", { userId, language });

    try {
      const ws = new WebSocket(USER_API);

      return new Promise((resolve, reject) => {
        ws.onopen = () => {
          console.log("📡 WebSocket opened for user fetch");
          const payload = {
            action: "getUser",
            user_id: userId,
            language: language
          };
          ws.send(JSON.stringify(payload));
        };

        ws.onmessage = (event) => {
          try {
            const response = JSON.parse(event.data);
            console.log("📩 Received user data response:", response);

            if (response.error) {
              reject(new Error(response.error));
              return;
            }

            // ✅ Map backend response to your existing userData structure
            const mappedUserData = {
              user_id: response.user?.user_id || '',
              username: response.user?.username || '',
              email: response.user?.Email || response.user?.email || '',
              zipcode: response.user?.Zipcode || response.user?.zipcode || '',
              phoneNumber: response.user?.Phone || response.user?.phoneNumber || '',
              language: response.language || 'english',
              referrals: response.user?.referrals || [],
              // ✅ Map feedback_questions to feedbackQuestions for your existing structure
              feedbackQuestions: response.feedback_questions || [],
              // ✅ Keep original field names for compatibility
              feedback_questions: response.feedback_questions || []
            };

            console.log("✅ Mapped user data for context:", mappedUserData);
            setUserData(prev => ({ ...prev, ...mappedUserData }));
            setIsLoading(false);
            ws.close();
            resolve(mappedUserData);

          } catch (error) {
            console.error("❌ Error parsing user data response:", error);
            setIsLoading(false);
            reject(error);
          }
        };

        ws.onerror = (error) => {
          console.error("❌ WebSocket error during user fetch:", error);
          setIsLoading(false);
          reject(error);
        };

        ws.onclose = (event) => {
          console.log("🔌 WebSocket closed after user fetch:", event.code);
          setIsLoading(false);
        };
      });

    } catch (error) {
      console.error("❌ Error fetching user data:", error);
      setIsLoading(false);
      throw error;
    }
  };

  useEffect(() => {
    console.log("📊 Updated User Context:", userData);
    console.log("🎯 Feedback Questions Count:", userData.feedbackQuestions?.length || 0);
  }, [userData]);

  return (
    <UserContext.Provider value={{
      userData,
      updateUser,
      fetchUserWithFeedback, // ✅ Add new function to context
      isLoading // ✅ Add loading state to context
    }}>
      {children}
    </UserContext.Provider>
  );
};

export const useUser = () => useContext(UserContext);