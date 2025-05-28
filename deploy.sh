#!/bin/bash
# deploy.sh - Deployment script for Brightpoint Stack

set -e  # Exit on error

# Color codes for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Function to print colored output
print_message() {
    echo -e "${2}${1}${NC}"
}

# Check if environment is provided
if [ -z "$1" ]; then
    print_message "Usage: ./deploy.sh <environment> [cdk-command]" $RED
    print_message "Environments: dev, test, prod" $YELLOW
    print_message "CDK Commands: synth, diff, deploy, destroy" $YELLOW
    exit 1
fi

ENV=$1
CDK_COMMAND=${2:-deploy}

# Validate environment
if [[ ! "$ENV" =~ ^(dev|test|prod)$ ]]; then
    print_message "Error: Invalid environment. Must be dev, test, or prod" $RED
    exit 1
fi

# Set environment variables
export CDK_ENV=$ENV

print_message "Starting deployment to $ENV environment..." $YELLOW

# Run CDK command
if [ "$CDK_COMMAND" == "deploy" ]; then
    print_message "Deploying stack to $ENV..." $GREEN
    npx cdk deploy -c env=$ENV --all --require-approval never
elif [ "$CDK_COMMAND" == "diff" ]; then
    print_message "Showing differences for $ENV..." $GREEN
    npx cdk diff -c env=$ENV --all
elif [ "$CDK_COMMAND" == "synth" ]; then
    print_message "Synthesizing stack for $ENV..." $GREEN
    npx cdk synth -c env=$ENV --all
elif [ "$CDK_COMMAND" == "destroy" ]; then
    print_message "Destroying stack in $ENV..." $RED
    read -p "Are you sure you want to destroy the $ENV stack? (y/N): " confirm
    if [[ $confirm == [yY] || $confirm == [yY][eE][sS] ]]; then
        npx cdk destroy -c env=$ENV --all --force
    else
        print_message "Destroy cancelled." $YELLOW
    fi
else
    print_message "Unknown command: $CDK_COMMAND" $RED
    exit 1
fi

print_message "Operation completed for $ENV!" $GREEN