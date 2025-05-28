import React, { createContext, useState, useContext, useEffect } from "react";
import { getCurrentUser } from 'aws-amplify/auth';
import { USER_API } from "./constants";

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

  const [isLoading, setIsLoading] = useState(false);

  const updateUser = (newData) => {
    setUserData((prev) => ({ ...prev, ...newData }));
  };

  const fetchUserWithFeedback = async (userId, language = 'english') => {
    setIsLoading(true);
    try {
      const ws = new WebSocket(USER_API);

      return new Promise((resolve, reject) => {
        ws.onopen = () => {
          const payload = {
            action: "getUser",
            user_id: userId,
            language
          };
          ws.send(JSON.stringify(payload));
        };

        ws.onmessage = (event) => {
          try {
            const response = JSON.parse(event.data);

            if (response.error) {
              reject(new Error(response.error));
              return;
            }

            const mappedUserData = {
              user_id: response.user?.user_id || '',
              username: response.user?.username || '',
              email: response.user?.Email || response.user?.email || '',
              zipcode: response.user?.Zipcode || response.user?.zipcode || '',
              phoneNumber: response.user?.Phone || response.user?.phoneNumber || '',
              language: response.user?.language || response.user?.Language || response.language || 'english',
              referrals: response.user?.referrals || [],
              feedbackQuestions: response.feedback_questions || [],
              feedback_questions: response.feedback_questions || []
            };

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

        ws.onclose = () => {
          setIsLoading(false);
        };
      });

    } catch (error) {
      console.error("❌ Error fetching user data:", error);
      setIsLoading(false);
      throw error;
    }
  };

  // ✅ Automatically fetch user on mount if logged in
  useEffect(() => {
    const checkUserSession = async () => {
      try {
        const currentUser = await getCurrentUser();
        const userId = currentUser?.attributes?.sub;
        const language = currentUser?.attributes?.locale || 'english';

        if (userId) {
          await fetchUserWithFeedback(userId, language);
        }
      } catch (err) {
        console.log("Not logged in or failed to fetch session:", err);
      }
    };

    checkUserSession();
  }, []);

  return (
    <UserContext.Provider value={{
      userData,
      updateUser,
      fetchUserWithFeedback,
      isLoading
    }}>
      {children}
    </UserContext.Provider>
  );
};

export const useUser = () => useContext(UserContext);
