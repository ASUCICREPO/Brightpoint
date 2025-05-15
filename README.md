# Brightpoint Referral Chatbot - Full Stack Application

This project contains a full-stack application for the Brightpoint Referral Chatbot, consisting of:
- A React frontend application
- AWS CDK backend infrastructure with Lambda functions, API Gateway, and DynamoDB

## Project Structure

```
Brightpoint/
├── backend_code/                    # AWS CDK infrastructure
│   ├── __pycache__/
│   └── brightpoint/                # Main application package
│       ├── __pycache__/
│       ├── perplexity_lambda/       # Lambda for Perplexity API integration
│       ├── process_user_data/       # Lambda for user data processing
│       ├── query_analytics_api/     # Lambda for analytics API
│       ├── query_analytics_backfill/# Lambda for analytics backfill
│       ├── query_analytics_stream_proc/ # Lambda for analytics stream processing
│       ├── referral_chatbot/        # Lambda for chatbot functionality
│       ├── referrals_api_handler/   # Lambda for referrals API
│       ├── sms_chat_integration/    # Lambda for SMS integration
│       ├── __init__.py
│       ├── brightpoint_stack.py     # Main CDK stack definition
│       └── config.py               # Configuration file
│
└── frontend/                        # React application
    ├── amplify/                    # AWS Amplify configuration
    ├── build/                      # Production build output
    ├── node_modules/               # Node dependencies
    ├── public/                     # Static assets
    ├── src/                        # React source code
    ├── .DS_Store
    ├── .gitignore
    ├── README.md
    ├── package-lock.json
    └── package.json
```

## Prerequisites

### Backend Requirements
- AWS CLI configured with appropriate credentials
- Python 3.9 or newer (compatible with Python 3.12 used in Lambda)
- Node.js 14 or newer (required for CDK)
- AWS CDK Toolkit (`npm install -g aws-cdk`)
- Git LFS (Large File Storage)

### Frontend Requirements
- Node.js 14 or newer
- npm or yarn package manager

## Detailed Installation Instructions

### macOS Installation

#### 1. Install Homebrew (Package Manager)
```bash
/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"
```

#### 2. Install Git and Git LFS
```bash
# Install Git (usually comes pre-installed)
brew install git

# Install Git LFS
brew install git-lfs
git lfs install
```

#### 3. Install AWS CLI
```bash
# Install AWS CLI
brew install awscli

# Verify installation
aws --version

# Configure AWS credentials
aws configure
```

#### 4. Install Python 3.9+
```bash
# Install Python
brew install python@3.12

# Verify installation
python3 --version

# Install pip (usually comes with Python)
pip3 --version

# Install virtualenv
pip3 install virtualenv
```

#### 5. Install Node.js and npm
```bash
# Install Node.js (includes npm)
brew install node@20

# Or using Node Version Manager (nvm)
curl -o- https://raw.githubusercontent.com/nvm-sh/nvm/v0.39.0/install.sh | bash
source ~/.zshrc  # or ~/.bash_profile
nvm install 20
nvm use 20

# Verify installation
node --version
npm --version
```

#### 6. Install AWS CDK Toolkit
```bash
npm install -g aws-cdk

# Verify installation
cdk --version
```

### Windows Installation

#### 1. Install Chocolatey (Package Manager)
Open PowerShell as Administrator and run:
```powershell
Set-ExecutionPolicy Bypass -Scope Process -Force; [System.Net.ServicePointManager]::SecurityProtocol = [System.Net.ServicePointManager]::SecurityProtocol -bor 3072; iex ((New-Object System.Net.WebClient).DownloadString('https://community.chocolatey.org/install.ps1'))
```

#### 2. Install Git and Git LFS
```powershell
# Install Git
choco install git -y

# Install Git LFS
choco install git-lfs -y

# Initialize Git LFS (run in regular Command Prompt or PowerShell)
git lfs install
```

#### 3. Install AWS CLI
```powershell
# Install AWS CLI using MSI installer
# Download from: https://awscli.amazonaws.com/AWSCLIV2.msi
# Or use Chocolatey:
choco install awscli -y

# Verify installation (run in new terminal)
aws --version

# Configure AWS credentials
aws configure
```

#### 4. Install Python 3.9+
```powershell
# Install Python
choco install python312 -y

# Or download from https://www.python.org/downloads/

# Verify installation (run in new terminal)
python --version

# Install pip (usually comes with Python)
pip --version

# Install virtualenv
pip install virtualenv
```

#### 5. Install Node.js and npm
```powershell
# Install Node.js (includes npm)
choco install nodejs-lts -y

# Or download from https://nodejs.org/

# Verify installation (run in new terminal)
node --version
npm --version
```

#### 6. Install AWS CDK Toolkit
```powershell
npm install -g aws-cdk

# Verify installation
cdk --version
```

### Alternative Installation Methods

#### Using Package Managers

**macOS with MacPorts:**
```bash
# Install MacPorts from https://www.macports.org/
sudo port install git git-lfs python312 nodejs20 awscli
```

**Windows with Scoop:**
```powershell
# Install Scoop
iwr -useb get.scoop.sh | iex

# Install packages
scoop install git python nodejs aws
```

### Verifying All Prerequisites

After installation, verify all components are properly installed:

```bash
# Check versions
git --version
git lfs version
aws --version
python3 --version  # or python --version on Windows
node --version
npm --version
cdk --version
```

### Common Installation Issues

#### macOS
- **Command not found**: Add Homebrew to your PATH: `echo 'export PATH="/opt/homebrew/bin:$PATH"' >> ~/.zshrc`
- **Permission errors**: Use `sudo` when needed or fix npm permissions
- **Python conflicts**: Use `pyenv` or `virtualenv` to manage Python versions

#### Windows
- **Execution policy errors**: Run PowerShell as Administrator
- **Path issues**: Restart terminal after installations or manually add to PATH
- **Python not found**: Use `py` instead of `python` command
- **npm permissions**: Run Command Prompt as Administrator for global installs

## Deployment Instructions

**For DEV environment** (For other environments, replace `dev` with other environment names)

### 1. Clone the Project Repository

```bash
# Install Git LFS (choose your platform)
brew install git-lfs          # macOS
choco install git-lfs         # Windows

# Initialize Git LFS
git lfs install

# Clone the backend_code branch of the repository
git clone --branch backend_code https://github.com/ASUCICREPO/Brightpoint.git

# Change into the project directory
cd Brightpoint

# Pull large files tracked by Git LFS
git lfs pull
```

### 2. Configure AWS Profile

Create an AWS profile to access your account. You'll need your AWS Access Key ID, Secret Access Key, and optionally a Session Token.

**Option 1: Using AWS CLI Configure**
```bash
# Create a new profile named Sandbox2025
aws configure --profile Sandbox2025

# You'll be prompted to enter:
# AWS Access Key ID [None]: YOUR_ACCESS_KEY_ID
# AWS Secret Access Key [None]: YOUR_SECRET_ACCESS_KEY
# Default region name [None]: us-east-1
# Default output format [None]: json
```

**Option 2: Manual Configuration**

**macOS/Linux:**
```bash
# Create/edit the credentials file
mkdir -p ~/.aws
nano ~/.aws/credentials

# Add the following content:
[Sandbox2025]
aws_access_key_id = YOUR_ACCESS_KEY_ID
aws_secret_access_key = YOUR_SECRET_ACCESS_KEY

# Create/edit the config file
nano ~/.aws/config

# Add the following content:
[profile Sandbox2025]
region = us-east-1
output = json
```

**Windows:**
```powershell
# Create/edit the credentials file
notepad %USERPROFILE%\.aws\credentials

# Add the following content:
[Sandbox2025]
aws_access_key_id = YOUR_ACCESS_KEY_ID
aws_secret_access_key = YOUR_SECRET_ACCESS_KEY

# Create/edit the config file
notepad %USERPROFILE%\.aws\config

# Add the following content:
[profile Sandbox2025]
region = us-east-1
output = json
```

**If using temporary credentials (with session token):**
```ini
[Sandbox2025]
aws_access_key_id = YOUR_ACCESS_KEY_ID
aws_secret_access_key = YOUR_SECRET_ACCESS_KEY
aws_session_token = YOUR_SESSION_TOKEN
```

**Verify Profile Configuration:**
```bash
# List all configured profiles
aws configure list-profiles

# Test the profile
aws sts get-caller-identity --profile Sandbox2025
```

### 3. Deploy the AWS CDK Stack

With the AWS profile configured, deploy the CDK stack.

In the `Brightpoint/` directory run the following command:

```bash
cdk deploy --profile Sandbox2025 -c env=dev --all
```

The deployment will output various resources. Here's an example of what the outputs look like:

```
Outputs:
BrightpointStack-dev.AmplifyAppId = d1r0ryjeyn2vc4
BrightpointStack-dev.AmplifyAppUrl = https://frontend-code.d1r0ryjeyn2vc4.amplifyapp.com
BrightpointStack-dev.AmplifyConsoleUrl = https://us-east-1.console.aws.amazon.com/amplify/apps/d1r0ryjeyn2vc4
BrightpointStack-dev.CognitoIdentityPoolId = us-east-1:db165b14-7422-4590-8250-0b2a86d8a897
BrightpointStack-dev.CognitoUserPoolClientId = rg7j932b1v6f1mabupqcvvanq
BrightpointStack-dev.CognitoUserPoolDomain = https://brightpoint-dev.auth.us-east-1.amazoncognito.com
BrightpointStack-dev.CognitoUserPoolId = us-east-1_dQWsOJccF
BrightpointStack-dev.FrontendConfigSummary = {
  "environment": "dev",
  "region": "us-east-1",
  "amplifyAppId": "d1r0ryjeyn2vc4",
  "userPoolId": "us-east-1_dQWsOJccF",
  "userPoolClientId": "rg7j932b1v6f1mabupqcvvanq",
  "identityPoolId": "us-east-1:db165b14-7422-4590-8250-0b2a86d8a897"
}
BrightpointStack-dev.ReferralChatbotAPIUrl = https://hjboae8luf.execute-api.us-east-1.amazonaws.com/dev/
BrightpointStack-dev.createUserUrl = https://tcmn9ufece.execute-api.us-east-1.amazonaws.com/dev/
BrightpointStack-dev.UserDashboardAPIUrl = https://mheqo8o3d3.execute-api.us-east-1.amazonaws.com/dev/
... (additional outputs)

✨  Total time: ~2-3 minutes
```

Save these output values as you'll need them for the frontend configuration.

### 3. Configure Frontend Environment Variables

**macOS (Terminal)**
```bash
cd frontend
cat > .env << EOF
REACT_APP_ENVIRONMENT=dev
REACT_APP_USER_POOL_ID=<from-cdk-output>
REACT_APP_USER_POOL_CLIENT_ID=<from-cdk-output>
REACT_APP_IDENTITY_POOL_ID=<from-cdk-output>
REACT_APP_API_URL=<from-cdk-output>
EOF
```

**Windows (PowerShell)**
```powershell
cd frontend
@"
REACT_APP_ENVIRONMENT=dev
REACT_APP_USER_POOL_ID=<from-cdk-output>
REACT_APP_USER_POOL_CLIENT_ID=<from-cdk-output>
REACT_APP_IDENTITY_POOL_ID=<from-cdk-output>
REACT_APP_API_URL=<from-cdk-output>
"@ > .env
```

### 4. Build the Frontend

```bash
npm install
npm run build
```

A `build/` directory will be created. Zip the contents of the build directory by going inside the directory, selecting all files and zipping it to `build.zip`.

### 5. Upload Frontend to AWS Amplify

1. Open the Amplify Console using the link from the `AmplifyManualAppConsoleUrl` output from the CDK deployment.
2. Select the **dev** branch in the Amplify App.
3. Click **"Upload" → "Deploy without Git provider"**.
4. Select the `build.zip` file.
5. Click **Deploy**.

### 6. Final Testing

- Visit the deployed Amplify frontend URL from CDK outputs
- Sign up and log in using the app interface
- Test referral submissions and responses

### 7. Import Data to DynamoDB to referral_data table

- Ensure that the correct name of the referral_data={env} table is mentioned as per the environment

```bash
python3 importFromCSVtoDDBtables.py
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

## Updating Lambda Code

1. Update code in the respective directories:
   - `backend/brightpoint/referral_chatbot/` for referralChatbotLambda
   - `backend/brightpoint/process_user_data/` for ProcessUserData

2. Deploy changes:
```bash
cd backend
cdk deploy
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
