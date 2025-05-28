#!/bin/bash
set -e

# Paths - following the same pattern as the original script
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"
CONFIG_FILE="$PROJECT_ROOT/config/cdk-config.json"

# Function to execute AWS commands with conditional profile usage
aws_cmd() {
    local cmd="$1"
    if [ -n "$PROFILE" ] && [ "$PROFILE" != "null" ] && [ "$PROFILE" != "" ]; then
        eval "aws $cmd --profile $PROFILE"
    else
        eval "aws $cmd"
    fi
}

# Check if CDK config exists and read profile
if [ -f "$CONFIG_FILE" ]; then
    echo "📖 Reading profile from CDK configuration..."
    PROFILE=$(jq -r '.profile // empty' "$CONFIG_FILE")
    REGION=$(jq -r '.region // "us-east-1"' "$CONFIG_FILE")
    echo "✅ Found profile: ${PROFILE:-"(default)"}"
    echo "✅ Found region: $REGION"
else
    echo "⚠️  CDK config file not found: $CONFIG_FILE"
    echo "💡 Using default profile and region"
    PROFILE=""
    REGION="us-east-1"
fi

echo ""
echo "Setting up AWS profile '${PROFILE:-"default"}'..."

# Only configure if a specific profile is set
if [ -n "$PROFILE" ] && [ "$PROFILE" != "null" ] && [ "$PROFILE" != "" ]; then
    echo "Please enter your AWS credentials for profile '$PROFILE' when prompted:"
    aws configure --profile "$PROFILE"
else
    echo "Please enter your AWS credentials for default profile when prompted:"
    aws configure
fi

# Verify the profile was created successfully
echo "Verifying AWS profile..."
if aws_cmd "sts get-caller-identity" > /dev/null 2>&1; then
    echo "Profile '${PROFILE:-"default"}' configured successfully!"
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
aws_cmd "iam create-role \
  --role-name APIGatewayCloudWatchLogsRole \
  --assume-role-policy-document file://~/apigateway-logs-policy.json"

# Attach the policy to the role
echo "Attaching policy to the role..."
aws_cmd "iam put-role-policy \
  --role-name APIGatewayCloudWatchLogsRole \
  --policy-name APIGatewayCloudWatchLogsPolicy \
  --policy-document file://~/apigateway-logs-role-policy.json"

# Get the role ARN
echo "Getting the role ARN..."
ROLE_ARN=$(aws_cmd "iam get-role --role-name APIGatewayCloudWatchLogsRole --query 'Role.Arn' --output text")
echo "Role ARN: $ROLE_ARN"

# Set the CloudWatch Logs role ARN in API Gateway account settings
echo "Configuring API Gateway account settings..."
aws_cmd "apigateway update-account \
  --patch-operations op=replace,path=/cloudwatchRoleArn,value=$ROLE_ARN"

echo ""
echo "📋 Configuration Summary:"
echo "========================"
echo "Profile: ${PROFILE:-"(default)"}"
echo "Region: $REGION"
echo "Role ARN: $ROLE_ARN"
echo ""
echo "🎉 API Gateway CloudWatch Logs configuration completed successfully!"