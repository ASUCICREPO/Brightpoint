// src/utilities/handleLogin.js
import { USER_API } from './constants'; // This should be your wss:// URL

export const fetchAndStoreUserData = async (userId, updateUser) => {
  return new Promise((resolve, reject) => {
    const socket = new WebSocket(USER_API);

    socket.onopen = () => {
      socket.send(
        JSON.stringify({
          action: 'getUser',
          user_id: userId,
        })
      );
    };

    socket.onmessage = (event) => {
      try {
        const data = JSON.parse(event.data);

        if (data && data.user) {
          const {
            user_id,
            language,
            Zipcode,
            Phone,
            Email,
            referrals,
          } = data.user;

          const feedbackQuestions = data.feedback_questions || [];

          updateUser({
            user_id,
            language,
            zipcode: Zipcode,
            phoneNumber: Phone,
            email: Email,
            referrals,
            feedbackQuestions,
          });

          resolve(); // Success
        } else {
          console.warn('Unexpected response:', data);
          reject(new Error('Invalid user data'));
        }

        socket.close(); // Clean up connection
      } catch (err) {
        reject(err);
      }
    };

    socket.onerror = (error) => {
      console.error('WebSocket error:', error);
      reject(error);
    };
  });
};
