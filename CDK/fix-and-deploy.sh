#!/bin/bash

PROFILE="Sandbox2025"
REGION="us-east-1"
ACCOUNT_ID="216989103356"

echo "Step 1: Cleaning up failed stack..."
aws cloudformation delete-stack --stack-name BrightpointStack --profile $PROFILE
aws cloudformation wait stack-delete-complete --stack-name BrightpointStack --profile $PROFILE

echo "Step 2: Upgrading bootstrap stack..."
cdk bootstrap aws://$ACCOUNT_ID/$REGION --profile $PROFILE --force

echo "Step 3: Creating CloudWatch Logs role for API Gateway..."
cat > api-gateway-trust-policy.json << 'EOF'
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

aws iam create-role \
  --role-name api-gateway-cloudwatch-logs \
  --assume-role-policy-document file://api-gateway-trust-policy.json \
  --profile $PROFILE || echo "Role already exists"

aws iam attach-role-policy \
  --role-name api-gateway-cloudwatch-logs \
  --policy-arn arn:aws:iam::aws:policy/service-role/AmazonAPIGatewayPushToCloudWatchLogs \
  --profile $PROFILE

ROLE_ARN=$(aws iam get-role --role-name api-gateway-cloudwatch-logs --query 'Role.Arn' --output text --profile $PROFILE)

echo "Step 4: Setting CloudWatch role for API Gateway..."
aws apigateway update-account \
  --patch-operations op=replace,path=/cloudwatchRoleArn,value=$ROLE_ARN \
  --profile $PROFILE

echo "Step 5: Deploying CDK stack..."
cdk deploy --profile $PROFILE

echo "Deployment complete!"