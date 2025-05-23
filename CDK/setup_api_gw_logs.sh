#!/bin/bash

echo "Setting up AWS profile 'Brightpoint_User'..."
echo "Please enter your AWS credentials when prompted:"
aws configure --profile Brightpoint_User

# Verify the profile was created successfully
echo "Verifying AWS profile..."
if aws sts get-caller-identity --profile Brightpoint_User > /dev/null 2>&1; then
    echo "Profile 'Brightpoint_User' configured successfully!"
else
    echo "Error: Failed to configure AWS profile. Please check your credentials."
    exit 1
fi

# Create a file for the IAM policy
echo "Creating IAM policy documents..."
cat > ~/apigateway-logs-policy.json << 'EOF'
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Principal": {
        "Service": "apigateway.amazonaws.com"
      },
      "Action": "sts:AssumeRole"
    }
  ]
}
EOF

# Create a file for the role policy
cat > ~/apigateway-logs-role-policy.json << 'EOF'
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Action": [
        "logs:CreateLogGroup",
        "logs:CreateLogStream",
        "logs:DescribeLogGroups",
        "logs:DescribeLogStreams",
        "logs:PutLogEvents",
        "logs:GetLogEvents",
        "logs:FilterLogEvents"
      ],
      "Resource": "*"
    }
  ]
}
EOF

# Create the IAM role
echo "Creating IAM role for API Gateway CloudWatch Logs..."
aws iam create-role \
  --role-name APIGatewayCloudWatchLogsRole \
  --assume-role-policy-document file://~/apigateway-logs-policy.json \
  --profile Brightpoint_User

# Attach the policy to the role
echo "Attaching policy to the role..."
aws iam put-role-policy \
  --role-name APIGatewayCloudWatchLogsRole \
  --policy-name APIGatewayCloudWatchLogsPolicy \
  --policy-document file://~/apigateway-logs-role-policy.json \
  --profile Brightpoint_User

# Get the role ARN
echo "Getting the role ARN..."
ROLE_ARN=$(aws iam get-role --role-name APIGatewayCloudWatchLogsRole --query 'Role.Arn' --output text --profile Brightpoint_User)
echo "Role ARN: $ROLE_ARN"

# Set the CloudWatch Logs role ARN in API Gateway account settings
echo "Configuring API Gateway account settings..."
aws apigateway update-account \
  --patch-operations op=replace,path=/cloudwatchRoleArn,value=$ROLE_ARN \
  --profile Brightpoint_User

echo "API Gateway CloudWatch Logs configuration completed successfully!"