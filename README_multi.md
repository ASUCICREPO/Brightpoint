# Brightpoint Multi-Environment CDK Stack

This CDK stack deploys the Brightpoint Referral Chatbot infrastructure across multiple environments (dev, test, prod).

## Prerequisites

- Python 3.9+
- Node.js 14+
- AWS CLI configured with appropriate credentials
- CDK CLI installed (`npm install -g aws-cdk`)

## Installation

```bash
# Install dependencies
pip install -r requirements.txt
npm install -g aws-cdk

# Or use make
make install
```

## Project Structure

```
brightpoint/
├── brightpoint/
│   ├── __init__.py
│   ├── brightpoint_stack.py    # Main CDK stack
│   ├── config.py              # Environment configurations
│   └── ...
├── app.py                     # CDK app entry point
├── deploy.sh                  # Bash deployment script
├── deploy_all.py             # Python script for multi-env deployment
├── deploy_single.py          # Python script for single env deployment
├── Makefile                  # Make commands for deployment
├── cdk.json                  # CDK configuration
├── setup.py
└── requirements.txt
```

## Environment Configuration

The stack supports three environments:
- **dev**: Development environment with minimal resources
- **test**: Testing environment with moderate resources
- **prod**: Production environment with full resources

Configuration for each environment is defined in `brightpoint/config.py`.

## Deployment Commands

### Using Make (Recommended)

```bash
# Deploy to specific environment
make deploy-dev
make deploy-test
make deploy-prod

# Deploy to all environments
make deploy-all

# Show differences
make diff ENV=dev
make diff-all

# Synthesize CloudFormation templates
make synth ENV=test
make synth-all

# Destroy stack
make destroy ENV=dev
```

### Using Shell Script

```bash
# Make script executable
chmod +x deploy.sh

# Deploy to specific environment
./deploy.sh dev
./deploy.sh test deploy
./deploy.sh prod

# Show differences
./deploy.sh dev diff

# Synthesize
./deploy.sh test synth

# Destroy
./deploy.sh dev destroy
```

### Using Python Scripts

```bash
# Deploy to all environments
python deploy_all.py deploy

# Deploy with specific environments
python deploy_all.py deploy --environments dev test

# Show differences for all
python deploy_all.py diff

# Deploy single environment with options
python deploy_single.py dev --hotswap --verbose
```

### Using CDK Directly

```bash
# Deploy to specific environment
npx cdk deploy -c env=dev --all

# Show differences
npx cdk diff -c env=test --all

# Synthesize
npx cdk synth -c env=prod --all

# Destroy
npx cdk destroy -c env=dev --all
```

## Resource Naming Convention

All resources are named with environment suffixes:
- DynamoDB Tables: `TableName-{env}`
- Lambda Functions: `FunctionName-{env}`
- APIs: `APIName-{env}`
- IAM Roles: `RoleName-{env}`

## Environment-Specific Features

### Development (dev)
- Lower memory allocations for Lambda functions
- Shorter timeout values
- DynamoDB tables with DESTROY removal policy
- Full API Gateway logging

### Test (test)
- Moderate memory allocations
- Standard timeout values
- DynamoDB tables with RETAIN removal policy
- Full API Gateway logging

### Production (prod)
- Maximum memory allocations
- Extended timeout values
- DynamoDB tables with RETAIN removal policy
- Error-level API Gateway logging only

## First-Time Setup

1. Bootstrap CDK for each environment:
```bash
make bootstrap-all
# Or individually:
cdk bootstrap aws://216989103356/us-east-1 -c env=dev
cdk bootstrap aws://216989103356/us-east-1 -c env=test
cdk bootstrap aws://216989103356/us-east-1 -c env=prod
```

2. Deploy to dev first to test:
```bash
make deploy-dev
```

3. Once validated, deploy to test and prod:
```bash
make deploy-test
make deploy-prod
```

## Validation

Before deploying, validate your stack:
```bash
# Validate specific environment
make validate ENV=dev

# Validate all environments
make validate-all
```

## Troubleshooting

1. **Stack already exists error**: 
   - Each environment has a unique stack name: `BrightpointStack-{env}`
   - If you need to redeploy, first destroy the existing stack

2. **Permission errors**:
   - Ensure your AWS credentials have necessary permissions
   - Check IAM roles have correct policies

3. **Resource conflicts**:
   - All resources have environment suffixes to avoid conflicts
   - Check for any hardcoded resource names

## Clean Up

To remove stacks:
```bash
# Remove specific environment
make destroy ENV=dev

# Remove all environments (use with caution!)
python deploy_all.py destroy
```

## Security Notes

- API Keys and sensitive data should be stored in AWS Secrets Manager
- The Perplexity API key in the code should be moved to Secrets Manager for production
- Cross-account SNS permissions are configured for SMS integration

## Monitoring

Each environment creates:
- CloudWatch Log Groups for Lambda functions
- API Gateway access logs
- DynamoDB table metrics

Monitor through AWS Console or CloudWatch dashboards.