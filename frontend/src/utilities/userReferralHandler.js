import { USER_API } from './constants';
import { useUser } from '../utilities/UserContext'; // Import useUser hook

// userReferralHandler.js
export const handleReferralOnLogin = (userId, callback) => {
    const socket = new WebSocket(USER_API);
  
    socket.onopen = () => {
      console.log('WebSocket connected');
      const request = {
        action: 'getUser',
        user_id: userId
      };
      socket.send(JSON.stringify(request));
      console.log('Request sent:', request);
    };
  
    socket.onmessage = (event) => {
      const data = JSON.parse(event.data);
      console.log('Response received:', data);
  
      if (data && data.feedback_questions && data.feedback_questions.length > 0) {
        // Get the first five referrals (or fewer if there aren't enough)
        const firstFiveReferrals = data.feedback_questions.slice(0, 5).map(referral => ({
          referral_id: referral.referral_id,
          question: referral.question
        }));
  
        // Invoke the callback passing the list of referrals
        callback(firstFiveReferrals);
        console.log('Referral data returned to callback:', firstFiveReferrals);
      } else {
        console.error('Error: No valid referral data');
        callback([]); // return an empty array if there's no valid data
      }
    };
  
    socket.onerror = (error) => {
      console.error('WebSocket error:', error);
    };
  
    socket.onclose = (event) => {
      if (event.wasClean) {
        console.log('WebSocket closed cleanly');
      } else {
        console.error('WebSocket closed unexpectedly');
      }
    };
  };
  