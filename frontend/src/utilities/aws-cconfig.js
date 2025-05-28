import AWS from 'aws-sdk';

// Step 1: Configure AWS Region and Credentials

// If you want to directly set IAM credentials (not recommended for production):
AWS.config.update({
  region: 'us-west-2', // Your region
  credentials: new AWS.Credentials('ASIARSU7KS7ISC5ROGJW', 'bwEo+M8FP+Q+OBfoEnb80towi8LsWL/+tUb63AUF') // Replace with your IAM credentials
});
