#!/bin/bash

# Colors for better readability
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# Set AWS CLI profile
AWS_PROFILE="account-1087"  # Change if needed

# Output file for CDK-ready info
OUTPUT_FILE="rest-apis-cdk-info.txt"

echo -e "${BLUE}==== REST APIs (API Gateway) ====${NC}"

# Clear output file if it exists
> "$OUTPUT_FILE"

# Get REST APIs
rest_apis=$(aws apigateway get-rest-apis \
  --profile "$AWS_PROFILE" \
  --query 'items[*].[id,name,description,endpointConfiguration.types[0]]' \
  --output json)

# Check if result is not empty or null
if [[ "$rest_apis" != "null" && "$rest_apis" != "[]" ]]; then
  echo -e "Found ${GREEN}$(echo "$rest_apis" | jq length)${NC} REST APIs"
  
  # Add to output file
  echo "// REST API IDs for CDK" >> "$OUTPUT_FILE"
  echo "// Generated on $(date)" >> "$OUTPUT_FILE"
  echo "" >> "$OUTPUT_FILE"
  
  echo "$rest_apis" | jq -c '.[]' | while read -r api; do
    api_id=$(echo "$api" | jq -r '.[0]')
    api_name=$(echo "$api" | jq -r '.[1]')
    api_description=$(echo "$api" | jq -r '.[2]')
    endpoint_type=$(echo "$api" | jq -r '.[3]')
    
    echo -e "\n${YELLOW}REST API: $api_name${NC}"
    echo -e "  ID: ${GREEN}$api_id${NC}"
    echo -e "  Description: ${api_description:-None}"
    echo -e "  Endpoint Type: $endpoint_type"
    
    # Get stages for this API
    stages=$(aws apigateway get-stages \
      --rest-api-id "$api_id" \
      --profile "$AWS_PROFILE" \
      --query 'item[*].[stageName,deploymentId]' \
      --output json)
    
    echo -e "  ${BLUE}Stages:${NC}"
    if [[ "$stages" != "null" && "$stages" != "[]" ]]; then
      echo "$stages" | jq -c '.[]' | while read -r stage; do
        stage_name=$(echo "$stage" | jq -r '.[0]')
        deployment_id=$(echo "$stage" | jq -r '.[1]')
        
        echo -e "    - $stage_name (Deployment ID: $deployment_id)"
        echo -e "      Full URL: ${GREEN}https://$api_id.execute-api.$(aws configure get region --profile "$AWS_PROFILE").amazonaws.com/$stage_name${NC}"
      done
    else
      echo -e "    ${RED}No stages found${NC}"
    fi
    
    # Get all resources for the REST API
    resources=$(aws apigateway get-resources \
      --rest-api-id "$api_id" \
      --profile "$AWS_PROFILE" \
      --query 'items[*].[id,path,resourceMethods]' \
      --output json)
    
    echo -e "  ${BLUE}Resources:${NC}"
    # Check if resources exist
    if [[ "$resources" != "null" && "$resources" != "[]" ]]; then
      lambda_count=0
      
      echo "$resources" | jq -c '.[]' | while read -r resource; do
        resource_id=$(echo "$resource" | jq -r '.[0]')
        path=$(echo "$resource" | jq -r '.[1]')
        methods=$(echo "$resource" | jq -r '.[2] | keys[]' 2>/dev/null)
        
        # Show all resources first
        echo -e "    - $path (ID: $resource_id)"
        
        # Process each method for this resource
        if [[ ! -z "$methods" ]]; then
          for method in $methods; do
            echo -e "      → Method: ${GREEN}$method${NC}"
            
            # Get method details including integration
            method_details=$(aws apigateway get-method \
              --rest-api-id "$api_id" \
              --resource-id "$resource_id" \
              --http-method "$method" \
              --profile "$AWS_PROFILE")
              
            integration_type=$(echo "$method_details" | jq -r '.methodIntegration.type // "NONE"')
            integration_uri=$(echo "$method_details" | jq -r '.methodIntegration.uri // "NONE"')
            
            echo -e "        Type: $integration_type"
            
            if [[ "$integration_uri" == *"arn:aws:lambda"* ]]; then
              ((lambda_count++))
              # Extract just the function name from ARN
              function_name=$(echo "$integration_uri" | awk -F: '{print $7}')
              echo -e "        → Lambda: ${GREEN}$function_name${NC}"
            elif [[ "$integration_uri" != "NONE" ]]; then
              echo -e "        → Integration URI: $integration_uri"
            fi
          done
        else
          echo -e "      ${RED}No methods${NC}"
        fi
      done
      
      echo -e "  Found ${GREEN}$lambda_count${NC} Lambda integrations"
    else
      echo -e "    ${RED}No resources found${NC}"
    fi
    
    # Generate CDK-friendly code for this API
    echo "// For API: $api_name (ID: $api_id)" >> "$OUTPUT_FILE"
    echo "const ${api_name//[^a-zA-Z0-9]/_}_rest_api_id = \"$api_id\";" >> "$OUTPUT_FILE"
    echo "" >> "$OUTPUT_FILE"
    echo "// In your CDK stack:" >> "$OUTPUT_FILE"
    echo "const ${api_name//[^a-zA-Z0-9]/_}_rest_api = new apigateway.RestApi(this, \"${api_name//[^a-zA-Z0-9]/_}RestApi\", {" >> "$OUTPUT_FILE"
    echo "  restApiId: ${api_name//[^a-zA-Z0-9]/_}_rest_api_id," >> "$OUTPUT_FILE"
    echo "  rootResourceId: /* Get the root resource ID for this API */," >> "$OUTPUT_FILE"
    echo "  endpointTypes: [apigateway.EndpointType.$endpoint_type]," >> "$OUTPUT_FILE"
    echo "  deployOptions: {" >> "$OUTPUT_FILE"
    echo "    stageName: \"prod\"," >> "$OUTPUT_FILE"
    echo "    description: \"Production stage\"" >> "$OUTPUT_FILE"
    echo "  }" >> "$OUTPUT_FILE"
    echo "});" >> "$OUTPUT_FILE"
    echo "" >> "$OUTPUT_FILE"
    echo "// Example of adding output:" >> "$OUTPUT_FILE"
    echo "new cdk.CfnOutput(this, \"${api_name//[^a-zA-Z0-9]/_}RestApiUrl\", {" >> "$OUTPUT_FILE"
    echo "  value: ${api_name//[^a-zA-Z0-9]/_}_rest_api.url," >> "$OUTPUT_FILE"
    echo "  description: \"URL of the ${api_name} REST API\"" >> "$OUTPUT_FILE"
    echo "});" >> "$OUTPUT_FILE"
    echo "" >> "$OUTPUT_FILE"
    echo "// ------------------------------------------------------" >> "$OUTPUT_FILE"
    echo "" >> "$OUTPUT_FILE"
  done
  
  echo -e "\n${GREEN}CDK-ready information has been saved to ${OUTPUT_FILE}${NC}"
else
  echo -e "${RED}No REST APIs found.${NC}"
fi