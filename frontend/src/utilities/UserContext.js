import React, { createContext, useState, useContext, useEffect } from "react";
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
    // ✅ NEW: Add children and due date fields
    firstName: '',
    lastName: '',
    children_birth_dates: [],
    expected_due_date: null,
  });

  const [isLoading, setIsLoading] = useState(false);

  // Load user data from localStorage on initial mount
  useEffect(() => {
    const loadPersistedUserData = () => {
      try {
        // Check if user was explicitly logged out
        const wasLoggedOut = sessionStorage.getItem('userLoggedOut');
        if (wasLoggedOut === 'true') {
          // Don't load persisted data if user was logged out
          return;
        }

        const persistedUserData = localStorage.getItem('userData');
        if (persistedUserData) {
          const parsedData = JSON.parse(persistedUserData);
          // Only load if we have essential user information
          if (parsedData.username || parsedData.user_id) {
            setUserData(prev => ({ ...prev, ...parsedData }));
            console.log("Loaded persisted user data:", parsedData);
          }
        }
      } catch (error) {
        console.error("Error loading persisted user data:", error);
        // Clear corrupted data
        localStorage.removeItem('userData');
      }
    };

    loadPersistedUserData();
  }, []);

  const updateUser = (newData) => {
    const updatedData = { ...userData, ...newData };
    setUserData(updatedData);

    // Persist to localStorage whenever user data is updated
    try {
      localStorage.setItem('userData', JSON.stringify(updatedData));
    } catch (error) {
      console.error("Error persisting user data:", error);
    }
  };

  // Clear user data (for logout)
  const clearUser = () => {
    setUserData({
      user_id: '',
      username: '',
      email: '',
      zipcode: '',
      phoneNumber: '',
      language: '',
      referrals: [],
      feedbackQuestions: [],
      // ✅ NEW: Clear children and due date fields
      firstName: '',
      lastName: '',
      children_birth_dates: [],
      expected_due_date: null,
    });

    try {
      // Clear all stored data
      localStorage.removeItem('userData');
      sessionStorage.removeItem('feedbackModalDismissed');
      // Clear any other app-specific storage
      sessionStorage.clear();
      // Optional: Clear localStorage completely if needed
      // localStorage.clear();
    } catch (error) {
      console.error("Error clearing user data:", error);
    }
  };

  // Complete logout function
  const logout = async () => {
    try {
      // Import signOut dynamically to avoid issues
      const { signOut } = await import('aws-amplify/auth');

      // Set logout flag before clearing data
      sessionStorage.setItem('userLoggedOut', 'true');

      // Sign out from AWS Amplify
      await signOut();

      // Clear user data
      clearUser();

      console.log("User successfully logged out");
      return true;
    } catch (error) {
      console.error("Error during logout:", error);
      // Even if signOut fails, clear local data
      sessionStorage.setItem('userLoggedOut', 'true');
      clearUser();
      return true; // Return true to force logout locally
    }
  };

  // Function to fetch user data with feedback questions
  const fetchUserWithFeedback = async (userId, language = 'english') => {
    setIsLoading(true);

    try {
      const ws = new WebSocket(USER_API);

      return new Promise((resolve, reject) => {
        ws.onopen = () => {
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

            if (response.error) {
              reject(new Error(response.error));
              return;
            }

            // ✅ ENHANCED: Map backend response to include children and due date data
            const mappedUserData = {
              user_id: response.user?.user_id || userId,
              username: response.user?.username || userId,
              email: response.user?.Email || response.user?.email || '',
              zipcode: response.user?.Zipcode || response.user?.zipcode || '',
              phoneNumber: response.user?.Phone || response.user?.phoneNumber || '',
              language: response.user?.language || response.user?.Language || response.language || 'english',
              referrals: response.user?.referrals || [],
              feedbackQuestions: response.feedback_questions || [],
              feedback_questions: response.feedback_questions || [],
              // ✅ NEW: Map children and due date data from backend
              firstName: response.user?.FirstName || response.user?.firstName || '',
              lastName: response.user?.LastName || response.user?.lastName || '',
              children_birth_dates: response.user?.children_birth_dates || [],
              expected_due_date: response.user?.expected_due_date || null,
            };

            console.log("✅ Mapped user data with children info:", {
              children_count: mappedUserData.children_birth_dates.length,
              children_dates: mappedUserData.children_birth_dates,
              due_date: mappedUserData.expected_due_date,
              firstName: mappedUserData.firstName,
              lastName: mappedUserData.lastName
            });

            // Update state and persist to localStorage
            setUserData(prev => {
              const updatedData = { ...prev, ...mappedUserData };
              try {
                localStorage.setItem('userData', JSON.stringify(updatedData));
              } catch (error) {
                console.error("Error persisting user data:", error);
              }
              return updatedData;
            });

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
          setIsLoading(false);
        };
      });

    } catch (error) {
      console.error("❌ Error fetching user data:", error);
      setIsLoading(false);
      throw error;
    }
  };

  return (
    <UserContext.Provider value={{
      userData,
      updateUser,
      clearUser, // Add clear function for logout
      logout, // Add complete logout function
      fetchUserWithFeedback,
      isLoading
    }}>
      {children}
    </UserContext.Provider>
  );
};

export const useUser = () => useContext(UserContext);