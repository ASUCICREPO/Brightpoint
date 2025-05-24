/* eslint-disable */
// This ensures it uses the correct Cognito pools created by your CDK stack

const awsmobile = {
    aws_project_region: process.env.REACT_APP_REGION,
    aws_cognito_region: process.env.REACT_APP_REGION,

    aws_user_pools_id: process.env.REACT_APP_USER_POOL_ID,
    aws_user_pools_web_client_id: process.env.REACT_APP_USER_POOL_CLIENT_ID,
    aws_cognito_identity_pool_id: process.env.REACT_APP_IDENTITY_POOL_ID,
    authenticationFlowType: 'USER_SRP_AUTH',

    oauth: {
        domain: process.env.REACT_APP_USER_POOL_DOMAIN?.replace('https://', ''),
        scope: ['email', 'profile', 'openid'],
        redirectSignIn: process.env.REACT_APP_REDIRECT_SIGN_IN,
        redirectSignOut: process.env.REACT_APP_REDIRECT_SIGN_OUT,
        responseType: 'code'
    },

    aws_cloud_logic_custom: [
        {
            name: 'BrightpointAPI',
            endpoint: process.env.REACT_APP_USER_ADD_API,
            region: process.env.REACT_APP_REGION
        }
    ]
};

console.log("🔧 AWS Exports Configuration:");
console.log("User Pool ID:", awsmobile.aws_user_pools_id);
console.log("Client ID:", awsmobile.aws_user_pools_web_client_id);
console.log("Identity Pool ID:", awsmobile.aws_cognito_identity_pool_id);
console.log("Region:", awsmobile.aws_project_region);

if (!awsmobile.aws_user_pools_id) {
    console.error("CRITICAL: Missing REACT_APP_USER_POOL_ID environment variable!");
    console.error("Make sure your CDK stack has deployed and set Amplify environment variables.");
}

if (!awsmobile.aws_user_pools_web_client_id) {
    console.error("CRITICAL: Missing REACT_APP_USER_POOL_CLIENT_ID environment variable!");
}

export default awsmobile;