// utilities/cognitoSignUp.js
import { CognitoIdentityProviderClient, SignUpCommand } from "@aws-sdk/client-cognito-identity-provider";

const REGION = "us-east-1"; // Replace with your region
const CLIENT_ID = "7t7kfj020k170b00sjolrpec74"; // Replace with your Cognito App Client ID

const client = new CognitoIdentityProviderClient({ region: REGION });

export const signUpUser = async (username, password) => {
  const command = new SignUpCommand({
    ClientId: CLIENT_ID,
    Username: username,
    Password: password,
    // Add additional attributes if needed
    // UserAttributes: [
    //   { Name: "email", Value: email }
    // ],
  });

  try {
    const response = await client.send(command);
    return { success: true, response };
  } catch (error) {
    console.error("Cognito sign-up error:", error);
    return { success: false, error };
  }
};
