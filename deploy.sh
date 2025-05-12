#!/bin/bash

# Colors for output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

echo -e "${YELLOW}Brightpoint Referral Chatbot CDK Deployment Helper${NC}"
echo "----------------------------------------"

# Check if CDK is installed
if ! command -v cdk &> /dev/null; then
    echo -e "${RED}AWS CDK is not installed. Please install it with: npm install -g aws-cdk${NC}"
    exit 1
fi

# Check if virtual environment exists, if not create one
if [ ! -d "venv" ]; then
    echo -e "${YELLOW}Creating Python virtual environment...${NC}"
    python3 -m venv venv
    source venv/bin/activate
    pip install -r requirements.txt
else
    echo -e "${GREEN}Using existing virtual environment${NC}"
    source venv/bin/activate
fi

# Ensure dependencies are installed
echo -e "${YELLOW}Ensuring dependencies are up to date...${NC}"
pip install -r requirements.txt

# Check if CDK is bootstrapped
echo -e "${YELLOW}Checking if CDK is bootstrapped in your account...${NC}"
cdk doctor

# Display deployment options
echo ""
echo -e "${GREEN}Deployment Options:${NC}"
echo "1. Check differences (cdk diff)"
echo "2. Deploy stack (import existing resources)"
echo "3. Deploy stack (create new resources - WARNING: may conflict with existing resources)"
echo "4. Exit"

# Get user choice
read -p "Enter your choice (1-4): " choice

case $choice in
    1)
        echo -e "${YELLOW}Running cdk diff to show changes...${NC}"
        cdk diff
        ;;
    2)
        echo -e "${YELLOW}Deploying stack with imported resources...${NC}"
        # Make sure import options are uncommented and create options are commented
        # This is currently the default in brightpoint_stack.py

        echo -e "${YELLOW}Running cdk deploy...${NC}"
        cdk deploy --require-approval never

        echo -e "${GREEN}Deployment complete!${NC}"
        ;;
    3)
        echo -e "${RED}WARNING: This option will create new resources that may conflict with existing ones.${NC}"
        echo -e "${RED}You will need to manually update the stack code to uncomment the resource creation sections.${NC}"
        read -p "Are you sure you want to continue? (y/n): " confirm

        if [ "$confirm" == "y" ] || [ "$confirm" == "Y" ]; then
            echo -e "${YELLOW}Deploying stack with new resources...${NC}"
            echo -e "${YELLOW}Running cdk deploy...${NC}"
            cdk deploy --require-approval never

            echo -e "${GREEN}Deployment complete!${NC}"
        else
            echo -e "${YELLOW}Deployment canceled.${NC}"
        fi
        ;;
    4)
        echo -e "${YELLOW}Exiting without deployment.${NC}"
        exit 0
        ;;
    *)
        echo -e "${RED}Invalid choice. Exiting.${NC}"
        exit 1
        ;;
esac

echo ""
echo -e "${GREEN}Deployment process completed.${NC}"