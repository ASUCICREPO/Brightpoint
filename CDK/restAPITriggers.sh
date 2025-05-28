#!/bin/bash

# Save this as find-api-triggers.sh and make it executable with: chmod +x find-api-triggers.sh

AWS_PROFILE="account-1087"
FUNCTION_NAME="ProcessUserData"  # Change this to your function name
REGION="us-east-1"  # Change if needed

# Get function ARN
FUNCTION_ARN=$(AWS_PROFILE=$AWS_PROFILE aws lambda get-function --function-name $FUNCTION_NAME --region $REGION --query Configuration.FunctionArn --output text)

echo "Searching API Gateway triggers for function: $FUNCTION_NAME"
echo "Function ARN: $FUNCTION_ARN"
echo "Using AWS Profile: $AWS_PROFILE"
echo "----------------------------------------"

# Check Lambda's resource-based policy for API Gateway permissions
echo "Checking Lambda resource-based policy..."
POLICY=$(AWS_PROFILE=$AWS_PROFILE aws lambda get-policy --function-name $FUNCTION_NAME --region $REGION --query Policy --output text 2>/dev/null)

if [ -n "$POLICY" ]; then
    echo "$POLICY" | jq '.Statement[] | select(.Principal.Service == "apigateway.amazonaws.com")' 2>/dev/null
fi

echo "----------------------------------------"

# Check REST APIs
echo "Checking REST APIs..."
for api_id in $(AWS_PROFILE=$AWS_PROFILE aws apigateway get-rest-apis --region $REGION --query 'items[].id' --output text); do
    api_name=$(AWS_PROFILE=$AWS_PROFILE aws apigateway get-rest-api --rest-api-id $api_id --region $REGION --query 'name' --output text)
    echo "Checking API: $api_name ($api_id)"
    
    for resource_id in $(AWS_PROFILE=$AWS_PROFILE aws apigateway get-resources --rest-api-id $api_id --region $REGION --query 'items[].id' --output text); do
        resource_path=$(AWS_PROFILE=$AWS_PROFILE aws apigateway get-resource --rest-api-id $api_id --resource-id $resource_id --region $REGION --query 'path' --output text 2>/dev/null)
        
        # Get all methods for this resource
        methods=$(AWS_PROFILE=$AWS_PROFILE aws apigateway get-resource --rest-api-id $api_id --resource-id $resource_id --region $REGION --query 'resourceMethods' --output json 2>/dev/null)
        
        if [ "$methods" != "null" ] && [ "$methods" != "{}" ]; then
            for method in $(echo $methods | jq -r 'keys[]' 2>/dev/null); do
                integration=$(AWS_PROFILE=$AWS_PROFILE aws apigateway get-integration --rest-api-id $api_id --resource-id $resource_id --http-method $method --region $REGION 2>/dev/null)
                if echo $integration | grep -q $FUNCTION_ARN; then
                    echo "  ✓ Found REST API trigger:"
                    echo "    - API: $api_name ($api_id)"
                    echo "    - Path: $resource_path"
                    echo "    - Method: $method"
                fi
            done
        fi
    done
done

echo "----------------------------------------"

# Check HTTP APIs (v2)
echo "Checking HTTP APIs (v2)..."
for api_id in $(AWS_PROFILE=$AWS_PROFILE aws apigatewayv2 get-apis --region $REGION --query 'Items[].ApiId' --output text); do
    api_name=$(AWS_PROFILE=$AWS_PROFILE aws apigatewayv2 get-api --api-id $api_id --region $REGION --query 'Name' --output text)
    echo "Checking API: $api_name ($api_id)"
    
    integrations=$(AWS_PROFILE=$AWS_PROFILE aws apigatewayv2 get-integrations --api-id $api_id --region $REGION --output json)
    
    for integration_id in $(echo $integrations | jq -r '.Items[].IntegrationId' 2>/dev/null); do
        integration_uri=$(echo $integrations | jq -r ".Items[] | select(.IntegrationId==\"$integration_id\") | .IntegrationUri" 2>/dev/null)
        if [ "$integration_uri" = "$FUNCTION_ARN" ]; then
            integration_method=$(echo $integrations | jq -r ".Items[] | select(.IntegrationId==\"$integration_id\") | .IntegrationMethod" 2>/dev/null)
            echo "  ✓ Found HTTP API trigger:"
            echo "    - API: $api_name ($api_id)"
            echo "    - Integration ID: $integration_id"
            echo "    - Method: $integration_method"
        fi
    done
done