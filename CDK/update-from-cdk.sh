#!/bin/bash
set -e

# Paths
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"
CONFIG_FILE="$PROJECT_ROOT/config/cdk-config.json"
FRONTEND_DIR="$PROJECT_ROOT/frontend"
ENV_FILE="$FRONTEND_DIR/.env"

echo "🚀 Auto-configuring frontend from CDK..."
echo "Config file: $CONFIG_FILE"
echo ""

# Check if CDK config exists
if [ ! -f "$CONFIG_FILE" ]; then
    echo "❌ CDK config file not found: $CONFIG_FILE"
    echo "💡 This means either:"
    echo "   1. CDK hasn't been deployed yet"
    echo "   2. CDK deployment failed"
    echo "   3. CDK code needs the config writing section added"
    echo ""
    echo "🔧 Run CDK deployment first:"
    echo "   cd CDK && cdk deploy --context env=dev --context region=us-east-1 --context profile=your-profile-name"
    exit 1
fi

# Read CDK configuration
echo "📖 Reading CDK configuration..."
STACK_NAME=$(jq -r '.stackName' "$CONFIG_FILE")
REGION=$(jq -r '.region' "$CONFIG_FILE")
ENVIRONMENT=$(jq -r '.environment' "$CONFIG_FILE")
PROFILE=$(jq -r '.profile // empty' "$CONFIG_FILE")
LAST_UPDATED=$(jq -r '.lastUpdated' "$CONFIG_FILE")

echo "✅ CDK Configuration:"
echo "   Stack Name: $STACK_NAME"
echo "   Region: $REGION"
echo "   Environment: $ENVIRONMENT"
echo "   Profile: ${PROFILE:-"(default)"}"
echo "   Last Updated: $LAST_UPDATED"
echo ""

# Fixed get_output function using the exact working command pattern
get_output() {
    local output_key=$1

    # Build command exactly like the working manual command
    if [ -n "$PROFILE" ] && [ "$PROFILE" != "null" ] && [ "$PROFILE" != "" ]; then
        aws cloudformation describe-stacks \
            --stack-name "$STACK_NAME" \
            --region "$REGION" \
            --query "Stacks[0].Outputs[?OutputKey=='$output_key'].OutputValue" \
            --profile "$PROFILE" \
            --output text 2>/dev/null || echo ""
    else
        aws cloudformation describe-stacks \
            --stack-name "$STACK_NAME" \
            --region "$REGION" \
            --query "Stacks[0].Outputs[?OutputKey=='$output_key'].OutputValue" \
            --output text 2>/dev/null || echo ""
    fi
}

# Debug function to list all outputs
list_all_outputs() {
    echo "🔍 ALL AVAILABLE CDK OUTPUTS:"
    echo "================================"

    if [ -n "$PROFILE" ] && [ "$PROFILE" != "null" ] && [ "$PROFILE" != "" ]; then
        aws cloudformation describe-stacks \
            --stack-name "$STACK_NAME" \
            --region "$REGION" \
            --query 'Stacks[0].Outputs[*].{Key:OutputKey, Value:OutputValue}' \
            --profile "$PROFILE" \
            --output table
    else
        aws cloudformation describe-stacks \
            --stack-name "$STACK_NAME" \
            --region "$REGION" \
            --query 'Stacks[0].Outputs[*].{Key:OutputKey, Value:OutputValue}' \
            --output table
    fi
}

# Verify stack access function
verify_stack_access() {
    echo "🔍 Verifying stack access..."
    echo "Stack: $STACK_NAME"
    echo "Region: $REGION"
    echo "Profile: ${PROFILE:-"(default)"}"
    echo ""

    if [ -n "$PROFILE" ] && [ "$PROFILE" != "null" ] && [ "$PROFILE" != "" ]; then
        aws cloudformation describe-stacks \
            --stack-name "$STACK_NAME" \
            --region "$REGION" \
            --profile "$PROFILE" \
            --query 'Stacks[0].{Name:StackName, Status:StackStatus}' \
            --output table
    else
        aws cloudformation describe-stacks \
            --stack-name "$STACK_NAME" \
            --region "$REGION" \
            --query 'Stacks[0].{Name:StackName, Status:StackStatus}' \
            --output table
    fi

    if [ $? -eq 0 ]; then
        echo "✅ Stack access verified!"
        return 0
    else
        echo "❌ Cannot access stack"
        return 1
    fi
}

# Verify stack access before proceeding
if ! verify_stack_access; then
    echo "❌ Cannot access stack: $STACK_NAME"
    echo "💡 Check your AWS profile and permissions"
    echo ""
    echo "🔧 Try these commands to debug:"
    echo "   aws sts get-caller-identity --profile ${PROFILE:-default}"
    echo "   aws cloudformation list-stacks --region $REGION --profile ${PROFILE:-default}"
    exit 1
fi

# List all available outputs to see what we're working with
list_all_outputs
echo ""

# Auto-detect the actual stack name if the configured one doesn't exist (this shouldn't be needed now)
echo "🔍 Verifying stack exists..."
verify_cmd="aws cloudformation describe-stacks --stack-name \"$STACK_NAME\" --region \"$REGION\""
if [ -n "$PROFILE" ] && [ "$PROFILE" != "null" ] && [ "$PROFILE" != "" ]; then
    verify_cmd="$verify_cmd --profile $PROFILE"
fi

if ! eval "$verify_cmd &>/dev/null"; then
    echo "⚠️  Stack '$STACK_NAME' not found. Searching for similar stacks..."

    search_cmd="aws cloudformation list-stacks --stack-status-filter CREATE_COMPLETE UPDATE_COMPLETE --region \"$REGION\""
    if [ -n "$PROFILE" ] && [ "$PROFILE" != "null" ] && [ "$PROFILE" != "" ]; then
        search_cmd="$search_cmd --profile $PROFILE"
    fi

    ACTUAL_STACK=$(eval "$search_cmd --query \"StackSummaries[?contains(StackName, 'brightpoint') || contains(StackName, 'Brightpoint')].StackName\" --output text 2>/dev/null | head -1")

    if [ -n "$ACTUAL_STACK" ] && [ "$ACTUAL_STACK" != "None" ]; then
        echo "✅ Found actual stack: $ACTUAL_STACK"
        STACK_NAME="$ACTUAL_STACK"

        # Update the config file with the correct stack name
        jq --arg stack "$ACTUAL_STACK" '.stackName = $stack' "$CONFIG_FILE" > temp.json && mv temp.json "$CONFIG_FILE"
        echo "✅ Updated config with correct stack name: $ACTUAL_STACK"
    else
        echo "❌ No Brightpoint-related stacks found"
        echo "🔧 Available stacks:"
        eval "$search_cmd --query 'StackSummaries[*].[StackName,StackStatus]' --output table" 2>/dev/null || echo "   Could not list stacks"
        exit 1
    fi
fi

echo "📡 Fetching CDK outputs from stack: $STACK_NAME"
echo ""

# Get all values from CDK outputs with debug
echo "🔍 Fetching individual outputs:"

USER_POOL_ID=$(get_output "CognitoUserPoolId")
echo "CognitoUserPoolId: '$USER_POOL_ID'"

USER_POOL_CLIENT_ID=$(get_output "CognitoUserPoolClientId")
echo "CognitoUserPoolClientId: '$USER_POOL_CLIENT_ID'"

IDENTITY_POOL_ID=$(get_output "CognitoIdentityPoolId")
echo "CognitoIdentityPoolId: '$IDENTITY_POOL_ID'"

USER_POOL_DOMAIN=$(get_output "CognitoUserPoolDomain")
echo "CognitoUserPoolDomain: '$USER_POOL_DOMAIN'"

CHAT_API=$(get_output "ChatWebSocketAPI")
echo "ChatWebSocketAPI: '$CHAT_API'"

USER_API=$(get_output "UserWebSocketAPI")
echo "UserWebSocketAPI: '$USER_API'"

REFERRAL_MANAGEMENT_API=$(get_output "ReferralManagementWebSocketAPI")
echo "ReferralManagementWebSocketAPI: '$REFERRAL_MANAGEMENT_API'"

ANALYTICS_API=$(get_output "AnalyticsRestAPI")
echo "AnalyticsRestAPI: '$ANALYTICS_API'"

USER_ADD_API=$(get_output "UserAddRestAPI")
echo "UserAddRestAPI: '$USER_ADD_API'"

# Try alternative output key names if the main one is empty
if [ -z "$USER_ADD_API" ] || [ "$USER_ADD_API" = "None" ]; then
    echo "Trying alternative names for USER_ADD_API..."

    USER_ADD_API=$(get_output "UserAddAPI")
    echo "UserAddAPI: '$USER_ADD_API'"

    if [ -z "$USER_ADD_API" ] || [ "$USER_ADD_API" = "None" ]; then
        USER_ADD_API=$(get_output "NewUserSignupAPI")
        echo "NewUserSignupAPI: '$USER_ADD_API'"
    fi

    if [ -z "$USER_ADD_API" ] || [ "$USER_ADD_API" = "None" ]; then
        USER_ADD_API=$(get_output "UserAPI")
        echo "UserAPI: '$USER_ADD_API'"
    fi

    if [ -z "$USER_ADD_API" ] || [ "$USER_ADD_API" = "None" ]; then
        USER_ADD_API=$(get_output "RestApiUrl")
        echo "RestApiUrl: '$USER_ADD_API'"
    fi
fi

REFERRAL_CHATBOT_REST_API=$(get_output "ReferralChatbotRestAPI")
echo "ReferralChatbotRestAPI: '$REFERRAL_CHATBOT_REST_API'"

REFERRALS_REST_API=$(get_output "ReferralsRestAPI")
echo "ReferralsRestAPI: '$REFERRALS_REST_API'"

AMPLIFY_APP_ID=$(get_output "AmplifyAppId")
echo "AmplifyAppId: '$AMPLIFY_APP_ID'"

echo ""

# Validate required values
if [ -z "$USER_POOL_ID" ] || [ -z "$USER_POOL_CLIENT_ID" ]; then
    echo "❌ Error: Could not fetch required CDK outputs from stack: $STACK_NAME"
    echo "💡 This could be due to:"
    echo "   1. Stack deployment not completed successfully"
    echo "   2. Missing IAM permissions for CloudFormation access"
    echo "   3. Wrong AWS profile or region"
    echo ""
    echo "🔧 All outputs were shown above. Check if the required outputs exist."
    exit 1
fi

echo "✅ Successfully fetched Cognito configuration"

# Show warning if API endpoints are missing
MISSING_APIS=()
[ -z "$CHAT_API" ] && MISSING_APIS+=("CHAT_API")
[ -z "$USER_API" ] && MISSING_APIS+=("USER_API")
[ -z "$USER_ADD_API" ] && MISSING_APIS+=("USER_ADD_API")
[ -z "$ANALYTICS_API" ] && MISSING_APIS+=("ANALYTICS_API")

if [ ${#MISSING_APIS[@]} -gt 0 ]; then
    echo ""
    echo "⚠️  WARNING: The following API endpoints are missing:"
    for api in "${MISSING_APIS[@]}"; do
        echo "   - $api"
    done
    echo ""
    echo "💡 This means either:"
    echo "   1. Your CDK stack doesn't have API Gateway resources"
    echo "   2. Your CDK stack has APIs but doesn't export them as CloudFormation outputs"
    echo "   3. The output key names in the script don't match your CDK exports"
    echo ""
    echo "🔧 To fix this, check your CDK code for:"
    echo "   - API Gateway resources (RestApi, LambdaRestApi, etc.)"
    echo "   - CfnOutput statements that export the API URLs"
    echo ""
fi

# Debug information before creating .env file
echo ""
echo "🔧 DEBUG: Pre-.env creation checks"
echo "=================================="
echo "SCRIPT_DIR: $SCRIPT_DIR"
echo "PROJECT_ROOT: $PROJECT_ROOT"
echo "FRONTEND_DIR: $FRONTEND_DIR"
echo "ENV_FILE: $ENV_FILE"
echo ""

# Check if frontend directory exists
echo "Frontend directory exists: $([ -d "$FRONTEND_DIR" ] && echo "YES" || echo "NO")"
echo "Frontend directory path: $FRONTEND_DIR"

# Create frontend directory if it doesn't exist
if [ ! -d "$FRONTEND_DIR" ]; then
    echo "Creating frontend directory..."
    mkdir -p "$FRONTEND_DIR"
fi

# Check permissions
echo "Can write to frontend directory: $([ -w "$FRONTEND_DIR" ] && echo "YES" || echo "NO")"

# Check if .env file already exists
if [ -f "$ENV_FILE" ]; then
    echo "Existing .env file found - will be overwritten"
    echo "Current .env size: $(wc -c < "$ENV_FILE" 2>/dev/null || echo "unknown") bytes"
else
    echo "No existing .env file found - will create new one"
fi

echo ""
echo "🔧 DEBUG: Variable values to be written"
echo "======================================="
echo "ENVIRONMENT: '$ENVIRONMENT'"
echo "REGION: '$REGION'"
echo "USER_POOL_ID: '$USER_POOL_ID'"
echo "USER_POOL_CLIENT_ID: '$USER_POOL_CLIENT_ID'"
echo "USER_ADD_API: '$USER_ADD_API'"
echo ""

# Test writing a simple file first
echo "Testing basic file write..."
echo "test" > "$FRONTEND_DIR/test.txt"
if [ -f "$FRONTEND_DIR/test.txt" ]; then
    echo "✅ Basic file write works"
    rm "$FRONTEND_DIR/test.txt"
else
    echo "❌ Basic file write failed"
    exit 1
fi

# Create .env file using a robust approach
echo "📝 Creating $ENV_FILE..."
echo "Writing to: $ENV_FILE"

# Create the .env file content
ENV_CONTENT="# Generated automatically from CDK outputs on $(date)
# Stack: $STACK_NAME
# Environment: $ENVIRONMENT
# Profile: ${PROFILE:-"(default)"}

REACT_APP_ENVIRONMENT=$ENVIRONMENT
REACT_APP_REGION=$REGION
REACT_APP_USER_POOL_ID=$USER_POOL_ID
REACT_APP_USER_POOL_CLIENT_ID=$USER_POOL_CLIENT_ID
REACT_APP_IDENTITY_POOL_ID=$IDENTITY_POOL_ID
REACT_APP_USER_POOL_DOMAIN=$USER_POOL_DOMAIN
REACT_APP_CHAT_API=$CHAT_API
REACT_APP_USER_API=$USER_API
REACT_APP_REFERRAL_MANAGEMENT_API=$REFERRAL_MANAGEMENT_API
REACT_APP_ANALYTICS_API=$ANALYTICS_API
REACT_APP_USER_ADD_API=$USER_ADD_API
REACT_APP_REFERRAL_CHATBOT_REST_API=$REFERRAL_CHATBOT_REST_API
REACT_APP_REFERRALS_REST_API=$REFERRALS_REST_API
REACT_APP_AMPLIFY_APP_ID=$AMPLIFY_APP_ID"

# Write the content to the file
echo "$ENV_CONTENT" > "$ENV_FILE"

# Verify the file was created successfully
if [ -f "$ENV_FILE" ]; then
    echo "✅ .env file created successfully!"
    echo "File size: $(wc -c < "$ENV_FILE") bytes"
    echo "File lines: $(wc -l < "$ENV_FILE") lines"
    echo ""
    echo "📄 Created .env file content:"
    echo "============================="
    cat "$ENV_FILE"
    echo "============================="
else
    echo "❌ Failed to create .env file"
    echo "Checking if we can create it with alternative method..."

    # Try alternative method using printf
    printf "%s\n" "$ENV_CONTENT" > "$ENV_FILE"

    if [ -f "$ENV_FILE" ]; then
        echo "✅ .env file created with alternative method!"
    else
        echo "❌ All methods failed to create .env file"
        echo "Current directory: $(pwd)"
        echo "Directory permissions: $(ls -ld "$FRONTEND_DIR")"
        exit 1
    fi
fi

echo ""
echo "📋 Configuration Summary:"
echo "========================"
echo "Stack:           $STACK_NAME"
echo "Environment:     $ENVIRONMENT"
echo "Profile:         ${PROFILE:-"(default)"}"
echo "Region:          $REGION"
echo "User Pool ID:    $USER_POOL_ID"
echo "User Add API:    ${USER_ADD_API:-"(not configured)"}"
echo ""

if [ ${#MISSING_APIS[@]} -eq 0 ]; then
    echo "🎉 Frontend configuration updated successfully!"
    echo "💡 Next: cd frontend && npm run build"
else
    echo "⚠️  Frontend configuration updated with warnings!"
    echo "💡 Some API endpoints are missing. Your app may have limited functionality."
    echo "🔧 Check your CDK stack and add the missing API Gateway resources."
fi

echo ""
echo "🏁 Script completed successfully!"