import { USER_API } from './constants';

export const fetchAndStoreUserData = async (userId, updateUser) => {
  return new Promise((resolve) => {
    const socket = new WebSocket(USER_API);

    const fallbackUser = {
      user_id: userId,
      language: 'English',
      zipcode: '62701',
      phoneNumber: '(123) 456-7890',
      email: 'user@example.com',
      referrals: [],
      feedbackQuestions: [],
    };

    const timeout = setTimeout(() => {
      console.warn("WebSocket timeout. Using fallback user data.");
      updateUser(fallbackUser);
      resolve(); // ✅ don't reject
      socket.close();
    }, 3000);

    socket.onopen = () => {
      socket.send(JSON.stringify({
        action: 'getUser',
        user_id: userId,
      }));
    };

    socket.onmessage = (event) => {
      clearTimeout(timeout);

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
        } else {
          console.warn('WebSocket response missing user. Using fallback.');
          updateUser(fallbackUser);
        }
      } catch (err) {
        console.error('Error parsing user data:', err);
        updateUser(fallbackUser);
      }

      socket.close();
      resolve(); // ✅ always resolve
    };

    socket.onerror = (error) => {
      console.error('WebSocket error:', error);
      clearTimeout(timeout);
      updateUser(fallbackUser);
      resolve(); // ✅ no rejection
      socket.close();
    };
  });
};
