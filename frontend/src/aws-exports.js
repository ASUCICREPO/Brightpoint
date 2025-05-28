/* eslint-disable */
// frontend/src/aws-exports.js
const awsmobile = {
    aws_project_region: process.env.REACT_APP_REGION || 'us-east-1',
    aws_cognito_region: process.env.REACT_APP_REGION || 'us-east-1',
    aws_user_pools_id: process.env.REACT_APP_USER_POOL_ID,
    aws_user_pools_web_client_id: process.env.REACT_APP_USER_POOL_CLIENT_ID,
    aws_cognito_identity_pool_id: process.env.REACT_APP_IDENTITY_POOL_ID,
    authenticationFlowType: 'USER_SRP_AUTH',
};

// Debug logging
console.log("🔧 AWS Configuration from CDK:");
console.log("- User Pool ID:", awsmobile.aws_user_pools_id);
console.log("- Client ID:", awsmobile.aws_user_pools_web_client_id?.substring(0, 8) + "...");

export default awsmobile;