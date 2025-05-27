import { USER_API } from './constants';

export const fetchAndStoreUserData = async (userId, updateUser) => {
  return new Promise((resolve) => {
    const socket = new WebSocket(USER_API);

    const fallbackUser = {
      user_id: userId,
      username: '',
      language: 'english',
      zipcode: '',
      phoneNumber: '',
      email: '',
      referrals: [],
      feedbackQuestions: [],
    };

    const timeout = setTimeout(() => {
      console.warn("WebSocket timeout. Using fallback user data.");
      updateUser(fallbackUser);
      resolve();
      socket.close();
    }, 3000);

    socket.onopen = () => {
      socket.send(JSON.stringify({ action: 'getUser', user_id: userId }));
    };

    socket.onmessage = (event) => {
      clearTimeout(timeout);
    
      try {
        const data = JSON.parse(event.data);
    
        if (data && data.user) {
          const {
            user_id,
            username = '',
            language = '',
            Zipcode: zipcode = '',          // Notice 'Zipcode' from server
            Phone: phoneNumber = '',         // 'Phone' from server
            Email: email = '',               // 'Email' from server
            referrals = [],
          } = data.user;
    
          // Use feedback_questions from server (underscored)
          const formattedFeedback = (data.feedback_questions || []).map((q) => ({
            referral_id: q.referral_id,
            question: q.question,                  // Use the exact question string from server
            agency: q.agency || '',
            service_category: q.service_category || '',
          }));
    
          updateUser({
            user_id,
            username,
            language,
            zipcode,
            phoneNumber,
            email,
            referrals,
            feedbackQuestions: formattedFeedback,
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
      resolve();
    };
    

    socket.onerror = (error) => {
      console.error('WebSocket error:', error);
      clearTimeout(timeout);
      updateUser(fallbackUser);
      resolve();
      socket.close();
    };
  });
};
