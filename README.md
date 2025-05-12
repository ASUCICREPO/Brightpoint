# Brightpoint Referral Chatbot CDK

This project contains an AWS CDK application that defines the infrastructure for the Brightpoint Referral Chatbot. It's designed to safely manage the existing Lambda functions, API Gateway, and related resources using Infrastructure as Code without disrupting the current flow.

## Project Structure

```
brightpoint/
├── app.py                      # Main CDK app entry point
├── requirements.txt            # Python dependencies
├── setup.py                    # Package setup for CDK
├── cdk.json                    # CDK configuration
├── deploy.sh                   # Helper script for deployment
└── brightpoint/
    ├── __init__.py
    ├── brightpoint_stack.py    # Main stack definition
    ├── referral_chatbot/       # Lambda code directory for referralChatbotLambda
    │   ├── referralChatbotLambda.py
    │   ├── bedrockAgent.py     # Helper module
    │   └── getServiceCategories.py # Helper module
    └── process_user_data/      # Lambda code directory for ProcessUserData
        └── lambda_function.py  # ProcessUserData handler file
```

## Prerequisites

- AWS CLI configured with appropriate credentials
- Python 3.9 or newer (compatible with Python 3.12 used in Lambda)
- Node.js 14 or newer (required for CDK)
- AWS CDK Toolkit (`npm install -g aws-cdk`)

## Setup

1. Clone this repository
2. Create and activate a virtual environment:

```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install dependencies:

```bash
pip install -r requirements.txt
```

4. If this is your first time using CDK in your AWS account/region, bootstrap the environment:

```bash
cdk bootstrap
```

## Deployment Options

This CDK project offers two main deployment approaches:

### Option 1: Import Existing Resources (Recommended)

The default implementation imports your existing Lambda functions, API Gateway endpoints, and DynamoDB tables, allowing you to manage infrastructure with CDK without recreating everything. This is the safest option and won't disrupt your current setup.

To deploy with this option:

```bash
./deploy.sh
# Then select option 2
```

### Option 2: Create New Resources

If you want to create new resources instead of importing existing ones:

1. Edit `brightpoint_stack.py` to:
   - Uncomment the Lambda function creation code
   - Uncomment the IAM role creation code
   - Uncomment the API Gateway resource creation code
   - Comment out the resource import code
2. Deploy using the script:

```bash
./deploy.sh
# Then select option 3
```

**Warning**: This option will attempt to create new Lambda functions with the same names as your existing ones, which will cause conflicts. You may need to rename resources or delete existing ones first.

## Current Infrastructure Reference

The CDK code imports these existing resources:

- Lambda Functions:
  - `referralChatbotLambda` (with helper modules: bedrockAgent.py and getServiceCategories.py)
  - `perplexityLambda`
  - `ProcessUserData`
  - `query-analytics-api`
  - `ReferralsApiHandler`

- REST APIs:
  - `ReferralChatbotAPI` (ID: pncxzrq0r9)
  - `createUser` (ID: kahgke45yd)
  - `UserDashboardAPI` (ID: 329yd7xxm0)
  - `QueryAnalyticsAPI1` (ID: adt0bzrd3e)
  - `QueryAnalyticsAPI2` (ID: ite99ljw0b)
  - `ReferralsApi` (ID: twi9ghqfhl)

- WebSocket APIs: 
  - `ReferralChatbotWebSocket` (ID: lajngh4a22)
  - `UserFeedbackWebSocketAPI` (ID: p8ea1v23i0)
  - `AnalyticsWebSocketAPI` (ID: duqhouj11e)
  - `ReferralsWebSocketAPI` (ID: z0ebrmmyd0)

- DynamoDB Tables:
  - `WebSocketConnections`
  - `perplexity_query_cache`
  - `query_analytics`
  - `referral_data`
  - `user_data` (with Phone-index GSI)

## REST API Details

### ReferralChatbotAPI (ID: pncxzrq0r9)
- **Resources**:
  - `/chat` - POST method (Lambda: referralChatbotLambda)
- **Endpoint**: https://pncxzrq0r9.execute-api.us-east-1.amazonaws.com/dev/

### createUser (ID: kahgke45yd)
- **Resources**:
  - `/addUser` - POST method (Lambda: ProcessUserData)
- **Endpoint**: https://kahgke45yd.execute-api.us-east-1.amazonaws.com/dev/

### UserDashboardAPI (ID: 329yd7xxm0)
- **Resources**:
  - `/dashboard` - GET method
- **Endpoint**: https://329yd7xxm0.execute-api.us-east-1.amazonaws.com/dev/

### QueryAnalyticsAPI (ID: adt0bzrd3e)
- **Resources**:
  - `/analytics/all` - POST method
- **Endpoint**: https://adt0bzrd3e.execute-api.us-east-1.amazonaws.com/dev/

### QueryAnalyticsAPI (ID: ite99ljw0b)
- **Resources**:
  - `/analytics/queries` - POST method
- **Endpoint**: https://ite99ljw0b.execute-api.us-east-1.amazonaws.com/dev/

### ReferralsApi (ID: twi9ghqfhl)
- **Resources**:
  - `/referrals/{referral_id}` - GET, POST, PUT, DELETE methods
  - `/referrals/search` - POST method
  - `/referrals` - GET, POST, PUT, DELETE methods
- **Endpoint**: https://twi9ghqfhl.execute-api.us-east-1.amazonaws.com/dev/

## WebSocket API Details

### ReferralChatbotWebSocket (ID: lajngh4a22)
- **Lambda Integration**: referralChatbotLambda
- **Routes**: $connect, query, $disconnect
- **Endpoint**: wss://lajngh4a22.execute-api.us-east-1.amazonaws.com/dev

### UserFeedbackWebSocketAPI (ID: p8ea1v23i0)
- **Lambda Integration**: ProcessUserData
- **Routes**: $disconnect, sendFeedback, updateUser, getUser, $connect
- **Endpoint**: wss://p8ea1v23i0.execute-api.us-east-1.amazonaws.com/dev

### AnalyticsWebSocketAPI (ID: duqhouj11e)
- **Lambda Integration**: query-analytics-api
- **Routes**: $default, $connect, getAnalytics, $disconnect
- **Endpoint**: wss://duqhouj11e.execute-api.us-east-1.amazonaws.com/dev

### ReferralsWebSocketAPI (ID: z0ebrmmyd0)
- **Lambda Integration**: ReferralsApiHandler
- **Routes**: getReferrals, $connect, createReferral, searchReferrals, $default, updateReferral, $disconnect, deleteReferral, getReferral
- **Endpoint**: wss://z0ebrmmyd0.execute-api.us-east-1.amazonaws.com/dev

## DynamoDB Table Details

### WebSocketConnections
- **Partition Key**: connectionId (String)
- **Billing Mode**: PAY_PER_REQUEST

### perplexity_query_cache
- **Partition Key**: query_id (String)
- **Billing Mode**: PAY_PER_REQUEST

### query_analytics
- **Partition Key**: query_text (String)
- **Sort Key**: Zipcode (String)
- **Billing Mode**: PAY_PER_REQUEST

### referral_data
- **Partition Key**: referral_id (String)
- **Billing Mode**: PAY_PER_REQUEST

### user_data
- **Partition Key**: user_id (String)
- **Billing Mode**: PAY_PER_REQUEST
- **Stream**: NEW_AND_OLD_IMAGES
- **GSI**: Phone-index (Partition Key: Phone)

## Lambda Function Details

### referralChatbotLambda
- **Runtime**: Python 3.12
- **Memory**: 1024 MB
- **Timeout**: 900 seconds (15 minutes)
- **Handler**: referralChatbotLambda.lambda_handler
- **Helper Modules**:
  - bedrockAgent.py
  - getServiceCategories.py

### perplexityLambda
- **Runtime**: Python 3.12
- **Memory**: 2048 MB
- **Timeout**: 900 seconds (15 minutes)
- **Handler**: lambda_function.lambda_handler
- **Environment Variables**:
  - PERPLEXITY_API_KEY

### ProcessUserData
- **Runtime**: Python 3.12
- **Memory**: 1024 MB
- **Timeout**: 900 seconds (15 minutes)
- **Handler**: lambda_function.lambda_handler
- **API Gateway Integrations**:
  - REST API routes: addUser
  - WebSocket routes: $connect, $disconnect, sendFeedback, getUser, updateUser

### query-analytics-api
- **WebSocket Integration**: AnalyticsWebSocketAPI
- **Routes**: $default, $connect, getAnalytics, $disconnect

### ReferralsApiHandler
- **REST API Integration**: ReferralsApi
- **WebSocket Integration**: ReferralsWebSocketAPI
- **Routes**: getReferrals, $connect, createReferral, searchReferrals, $default, updateReferral, $disconnect, deleteReferral, getReferral

## Checking Infrastructure Differences

To see what changes will be applied before deploying:

```bash
./deploy.sh
# Then select option 1
```

Or directly:

```bash
cdk diff
```

## Updating Lambda Code

When you need to update Lambda function code:

1. Update the code in the respective directories:
   - `brightpoint/referral_chatbot/` for referralChatbotLambda
   - `brightpoint/process_user_data/` for ProcessUserData
2. Uncomment the Lambda function creation sections in `brightpoint_stack.py`
3. Run `cdk deploy` to update the functions

## Cleanup

If you need to remove CDK-managed resources:

```bash
cdk destroy
```

**Note**: Resources that were imported (not created by CDK) will not be affected by `cdk destroy`.

## Help and Troubleshooting

- If you're unsure about deployment, use the helper script:
  ```bash
  ./deploy.sh
  ```

- If you encounter permission issues, check the IAM role in `brightpoint_stack.py` against your AWS console permissions