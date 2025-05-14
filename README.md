# Brightpoint Referral Chatbot - Full Stack Application

This project contains a full-stack application for the Brightpoint Referral Chatbot, consisting of:
- A React frontend application
- AWS CDK backend infrastructure with Lambda functions, API Gateway, and DynamoDB

## Project Structure

```
brightpoint-project/
├── frontend/                   # React application
│   ├── public/
│   ├── src/
│   ├── package.json
│   └── README.md
│
└── backend/                    # AWS CDK infrastructure
    ├── app.py                 # Main CDK app entry point
    ├── requirements.txt       # Python dependencies
    ├── setup.py              # Package setup for CDK
    ├── cdk.json              # CDK configuration
    ├── deploy.sh             # Helper script for deployment
    └── brightpoint/
        ├── __init__.py
        ├── brightpoint_stack.py    # Main stack definition
        ├── referral_chatbot/       # Lambda code for referralChatbotLambda
        │   ├── referralChatbotLambda.py
        │   ├── bedrockAgent.py
        │   └── getServiceCategories.py
        └── process_user_data/      # Lambda code for ProcessUserData
            └── lambda_function.py
```

## Prerequisites

### Backend Requirements
- AWS CLI configured with appropriate credentials
- Python 3.9 or newer (compatible with Python 3.12 used in Lambda)
- Node.js 14 or newer (required for CDK)
- AWS CDK Toolkit (`npm install -g aws-cdk`)

### Frontend Requirements
- Node.js 14 or newer
- npm or yarn package manager

## Setup

### Backend Setup

1. Navigate to the backend directory:
```bash
cd backend
```

2. Create and activate a virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install Python dependencies:
```bash
pip install -r requirements.txt
```

4. If this is your first time using CDK in your AWS account/region, bootstrap:
```bash
cdk bootstrap
```

### Frontend Setup

1. Navigate to the frontend directory:
```bash
cd frontend
```

2. Install dependencies:
```bash
npm install
# or
yarn install
```

## Development

### Frontend Development

In the frontend directory, you can run:

#### `npm start`
Runs the app in development mode. Open [http://localhost:3000](http://localhost:3000) to view it in your browser. The page will reload on changes.

#### `npm test`
Launches the test runner in interactive watch mode.

#### `npm run build`
Builds the app for production to the `build` folder. The build is minified and optimized for best performance.

#### `npm run eject`
**Note: this is a one-way operation. Once you `eject`, you can't go back!**

Removes the single build dependency and copies all configuration files and dependencies directly into your project for full control.

### Backend Development

The backend uses AWS CDK to manage infrastructure. The project imports existing AWS resources to avoid disruption to current services.

#### Checking Infrastructure Changes
```bash
cd backend
./deploy.sh
# Then select option 1
```

Or directly:
```bash
cdk diff
```

## Deployment

### Backend Deployment

The CDK project offers two deployment approaches:

#### Option 1: Import Existing Resources (Recommended)
This is the safest option that won't disrupt your current setup.
```bash
cd backend
./deploy.sh
# Then select option 2
```

#### Option 2: Create New Resources
**Warning**: This option will attempt to create new Lambda functions with the same names as existing ones, which may cause conflicts.

1. Edit `brightpoint_stack.py` to:
   - Uncomment Lambda function creation code
   - Uncomment IAM role creation code
   - Uncomment API Gateway resource creation code
   - Comment out resource import code
2. Deploy:
```bash
./deploy.sh
# Then select option 3
```

### Frontend Deployment

Build the React application:
```bash
cd frontend
npm run build
```

The `build` folder can then be deployed to your preferred hosting service (AWS S3 with CloudFront, Vercel, Netlify, etc.).

## Backend Infrastructure Details

### Lambda Functions
- **referralChatbotLambda**
  - Runtime: Python 3.12
  - Memory: 1024 MB
  - Timeout: 900 seconds (15 minutes)
  - Handler: referralChatbotLambda.lambda_handler
  - Helper Modules: bedrockAgent.py, getServiceCategories.py

- **perplexityLambda**
  - Runtime: Python 3.12
  - Memory: 2048 MB
  - Timeout: 900 seconds
  - Environment Variables: PERPLEXITY_API_KEY

- **ProcessUserData**
  - Runtime: Python 3.12
  - Memory: 1024 MB
  - Timeout: 900 seconds
  - Handler: lambda_function.lambda_handler

- **query-analytics-api**
- **ReferralsApiHandler**

### API Endpoints

#### REST APIs
- **ReferralChatbotAPI**: `https://pncxzrq0r9.execute-api.us-east-1.amazonaws.com/dev/`
  - `/chat` - POST (Main chatbot endpoint)

- **createUser**: `https://kahgke45yd.execute-api.us-east-1.amazonaws.com/dev/`
  - `/addUser` - POST (User creation)

- **UserDashboardAPI**: `https://329yd7xxm0.execute-api.us-east-1.amazonaws.com/dev/`
  - `/dashboard` - GET

- **QueryAnalyticsAPI**:
  - `https://adt0bzrd3e.execute-api.us-east-1.amazonaws.com/dev/`
    - `/analytics/all` - POST
  - `https://ite99ljw0b.execute-api.us-east-1.amazonaws.com/dev/`
    - `/analytics/queries` - POST

- **ReferralsApi**: `https://twi9ghqfhl.execute-api.us-east-1.amazonaws.com/dev/`
  - `/referrals` - GET, POST, PUT, DELETE
  - `/referrals/{referral_id}` - GET, POST, PUT, DELETE
  - `/referrals/search` - POST

#### WebSocket APIs
- **ReferralChatbotWebSocket**: `wss://lajngh4a22.execute-api.us-east-1.amazonaws.com/dev`
  - Routes: $connect, query, $disconnect

- **UserFeedbackWebSocketAPI**: `wss://p8ea1v23i0.execute-api.us-east-1.amazonaws.com/dev`
  - Routes: $disconnect, sendFeedback, updateUser, getUser, $connect

- **AnalyticsWebSocketAPI**: `wss://duqhouj11e.execute-api.us-east-1.amazonaws.com/dev`
  - Routes: $default, $connect, getAnalytics, $disconnect

- **ReferralsWebSocketAPI**: `wss://z0ebrmmyd0.execute-api.us-east-1.amazonaws.com/dev`
  - Routes: getReferrals, $connect, createReferral, searchReferrals, updateReferral, deleteReferral, getReferral

### DynamoDB Tables
- **WebSocketConnections**
  - Partition Key: connectionId (String)
  - Billing Mode: PAY_PER_REQUEST

- **perplexity_query_cache**
  - Partition Key: query_id (String)
  - Billing Mode: PAY_PER_REQUEST

- **query_analytics**
  - Partition Key: query_text (String)
  - Sort Key: Zipcode (String)
  - Billing Mode: PAY_PER_REQUEST

- **referral_data**
  - Partition Key: referral_id (String)
  - Billing Mode: PAY_PER_REQUEST

- **user_data**
  - Partition Key: user_id (String)
  - Billing Mode: PAY_PER_REQUEST
  - Stream: NEW_AND_OLD_IMAGES

## Configuration

### Frontend Environment Variables
Create a `.env` file in the frontend directory:
```
REACT_APP_API_ENDPOINT=https://pncxzrq0r9.execute-api.us-east-1.amazonaws.com/dev
REACT_APP_WEBSOCKET_ENDPOINT=wss://lajngh4a22.execute-api.us-east-1.amazonaws.com/dev
REACT_APP_USER_API_ENDPOINT=https://kahgke45yd.execute-api.us-east-1.amazonaws.com/dev
REACT_APP_DASHBOARD_API_ENDPOINT=https://329yd7xxm0.execute-api.us-east-1.amazonaws.com/dev
```

### Updating Lambda Code

1. Update code in the respective directories:
   - `backend/brightpoint/referral_chatbot/` for referralChatbotLambda
   - `backend/brightpoint/process_user_data/` for ProcessUserData

2. Deploy changes:
```bash
cd backend
cdk deploy
```

## Advanced Frontend Configuration

### Code Splitting
The React app supports code splitting. See: [Create React App - Code Splitting](https://facebook.github.io/create-react-app/docs/code-splitting)

### Analyzing Bundle Size
See: [Create React App - Analyzing Bundle Size](https://facebook.github.io/create-react-app/docs/analyzing-the-bundle-size)

### Progressive Web App
For PWA configuration: [Create React App - Making a Progressive Web App](https://facebook.github.io/create-react-app/docs/making-a-progressive-web-app)

### Advanced Configuration
See: [Create React App - Advanced Configuration](https://facebook.github.io/create-react-app/docs/advanced-configuration)

## Cleanup

### Backend Cleanup
Remove CDK-managed resources:
```bash
cd backend
cdk destroy
```
**Note**: Resources that were imported (not created by CDK) will not be affected by `cdk destroy`.

### Frontend Cleanup
Remove node_modules and build artifacts:
```bash
cd frontend
rm -rf node_modules build
```

## Troubleshooting

### Backend Issues
- **Permission errors**: Check IAM roles in `brightpoint_stack.py` against your AWS console permissions
- **Deployment failures**: Run `cdk diff` to check what changes will be applied
- **General help**: Use the helper script for guided deployment: `./deploy.sh`

### Frontend Issues
- **Build failures**: See [npm run build fails to minify](https://facebook.github.io/create-react-app/docs/troubleshooting#npm-run-build-fails-to-minify)
- **Runtime errors**: Check browser console and verify API endpoints in `.env`
- **Test issues**: See [running tests](https://facebook.github.io/create-react-app/docs/running-tests)

## Learn More

### Frontend Resources
- [Create React App documentation](https://facebook.github.io/create-react-app/docs/getting-started)
- [React documentation](https://reactjs.org/)

### Backend Resources
- [AWS CDK documentation](https://docs.aws.amazon.com/cdk/latest/guide/home.html)
- [AWS Lambda documentation](https://docs.aws.amazon.com/lambda/)
- [AWS API Gateway documentation](https://docs.aws.amazon.com/apigateway/)
- [AWS DynamoDB documentation](https://docs.aws.amazon.com/dynamodb/)

## License

This project is proprietary to Brightpoint.

## Support

For infrastructure questions or issues, check the helper script:
```bash
cd backend
./deploy.sh
```

For application-specific issues, consult the respective frontend or backend documentation.