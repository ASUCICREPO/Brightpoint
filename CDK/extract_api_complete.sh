#!/bin/bash

# Script to extract API Gateway configurations and generate complete CDK code
# Usage: ./extract_api_complete.sh [--region us-east-1] [--profile default] [--output api_gateway_complete.py]

# Default values
REGION="us-east-1"
PROFILE="default"
OUTPUT_FILE="api_gateway_complete.py"

# Parse command line arguments
while [[ $# -gt 0 ]]; do
    case $1 in
        --region)
            REGION="$2"
            shift 2
            ;;
        --profile)
            PROFILE="$2"
            shift 2
            ;;
        --output)
            OUTPUT_FILE="$2"
            shift 2
            ;;
        *)
            echo "Unknown option: $1"
            exit 1
            ;;
    esac
done

# Common AWS CLI options
AWS_OPTS="--region $REGION --profile $PROFILE --output json"

echo "Extracting API Gateway configurations..."
echo "Region: $REGION"
echo "Profile: $PROFILE"
echo "Output File: $OUTPUT_FILE"
echo "----------------------------------------"

# Initialize the output file
cat > "$OUTPUT_FILE" << 'EOF'
# Complete API Gateway CDK Configuration
# Add this code to your brightpoint_stack.py

from aws_cdk import (
    Stack,
    aws_apigateway as apigateway,
    aws_apigatewayv2 as apigatewayv2,
    aws_apigatewayv2_integrations as integrations,
    aws_lambda as lambda_,
    aws_iam as iam,
    CfnOutput,
    Duration,
)
from constructs import Construct


class ApiGatewayComplete:
    """Complete API Gateway configuration for BrightpointStack"""
    
    def __init__(self, scope: Stack, account_id: str):
        self.scope = scope
        self.account_id = account_id
        
        # Lambda functions mapping
        self.lambda_functions = {
            'referralChatbotLambda': lambda_.Function.from_function_name(
                scope, "ReferralChatbotLambdaFn", "referralChatbotLambda"
            ),
            'perplexityLambda': lambda_.Function.from_function_name(
                scope, "PerplexityLambdaFn", "perplexityLambda"
            ),
            'ProcessUserData': lambda_.Function.from_function_name(
                scope, "ProcessUserDataFn", "ProcessUserData"
            ),
            'query-analytics-api': lambda_.Function.from_function_name(
                scope, "QueryAnalyticsApiFn", "query-analytics-api"
            ),
            'ReferralsApiHandler': lambda_.Function.from_function_name(
                scope, "ReferralsApiHandlerFn", "ReferralsApiHandler"
            ),
        }
        
        # Store API references
        self.rest_apis = {}
        self.websocket_apis = {}
        
        # Create all APIs
        self.create_all_apis()
    
    def create_all_apis(self):
        """Create all REST and WebSocket APIs"""
        self.create_rest_apis()
        self.create_websocket_apis()
        self.create_outputs()
        self.add_lambda_permissions()
    
    def create_rest_apis(self):
        """Create all REST APIs with complete configuration"""
        
EOF

# Function to clean variable names
clean_var_name() {
    local name=$1
    # Replace non-alphanumeric with underscore
    name=$(echo "$name" | sed 's/[^a-zA-Z0-9_]/_/g')
    # Ensure it starts with a letter
    if [[ $name =~ ^[0-9] ]]; then
        name="var_$name"
    fi
    echo "$name"
}

# Extract REST APIs
echo "Extracting REST APIs..."
rest_apis_json=$(aws apigateway get-rest-apis $AWS_OPTS)

# Check if we got valid JSON
if ! echo "$rest_apis_json" | jq -e . >/dev/null 2>&1; then
    echo "Error: Failed to get REST APIs list"
    exit 1
fi

# Get list of API IDs and names
api_count=$(echo "$rest_apis_json" | jq -r '.items | length')
echo "Found $api_count REST APIs"

# Process each REST API
for i in $(seq 0 $((api_count - 1))); do
    api_id=$(echo "$rest_apis_json" | jq -r ".items[$i].id")
    api_name=$(echo "$rest_apis_json" | jq -r ".items[$i].name")
    api_description=$(echo "$rest_apis_json" | jq -r ".items[$i].description // \"\"" | sed 's/"/\\"/g')
    
    echo "Processing REST API: $api_name ($api_id)"
    
    # Clean API name for variable use
    api_var_name=$(clean_var_name "$api_name")
    
    # Get stages
    stages_json=$(aws apigateway get-stages $AWS_OPTS --rest-api-id "$api_id")
    stage_name=$(echo "$stages_json" | jq -r '.item[0].stageName // "prod"')
    
    # Write API definition
    cat >> "$OUTPUT_FILE" << EOF
        # ${api_name} - Original ID: ${api_id}
        ${api_var_name}_api = apigateway.RestApi(
            self.scope, "${api_name}",
            rest_api_name="${api_name}",
            description="${api_description}",
            deploy_options=apigateway.StageOptions(
                stage_name="${stage_name}",
                logging_level=apigateway.MethodLoggingLevel.INFO,
                data_trace_enabled=True,
                metrics_enabled=True
            ),
            default_cors_preflight_options=apigateway.CorsOptions(
                allow_origins=apigateway.Cors.ALL_ORIGINS,
                allow_methods=apigateway.Cors.ALL_METHODS,
                allow_headers=["Content-Type", "X-Amz-Date", "Authorization", "X-Api-Key"]
            )
        )
        self.rest_apis['${api_name}'] = ${api_var_name}_api
        
EOF

    # Get resources for this API
    resources_json=$(aws apigateway get-resources $AWS_OPTS --rest-api-id "$api_id" --limit 500)
    
    if echo "$resources_json" | jq -e . >/dev/null 2>&1; then
        # Process resources
        resource_count=$(echo "$resources_json" | jq -r '.items | length')
        
        for j in $(seq 0 $((resource_count - 1))); do
            resource_path=$(echo "$resources_json" | jq -r ".items[$j].path")
            resource_id=$(echo "$resources_json" | jq -r ".items[$j].id")
            path_part=$(echo "$resources_json" | jq -r ".items[$j].pathPart // \"\"")
            
            if [ "$resource_path" != "/" ] && [ -n "$path_part" ]; then
                var_name=$(clean_var_name "${api_var_name}_${resource_path}")
                
                # Handle path parameters
                if [[ "$path_part" =~ ^\{.*\}$ ]]; then
                    path_part_value="$path_part"
                else
                    path_part_value="\"$path_part\""
                fi
                
                # Determine parent
                parent_path=$(dirname "$resource_path")
                if [ "$parent_path" = "/" ]; then
                    parent_var="${api_var_name}_api.root"
                else
                    parent_var=$(clean_var_name "${api_var_name}_${parent_path}")
                fi
                
                cat >> "$OUTPUT_FILE" << EOF
        # Resource: ${resource_path}
        ${var_name} = ${parent_var}.add_resource(${path_part_value})
EOF
                
                # Check for methods
                methods=$(echo "$resources_json" | jq -r ".items[$j].resourceMethods // {} | keys[]" 2>/dev/null)
                
                for method in $methods; do
                    if [ "$method" != "OPTIONS" ] && [ -n "$method" ]; then
                        # Get method details
                        method_json=$(aws apigateway get-method $AWS_OPTS --rest-api-id "$api_id" --resource-id "$resource_id" --http-method "$method" 2>/dev/null)
                        
                        if [ $? -eq 0 ] && echo "$method_json" | jq -e . >/dev/null 2>&1; then
                            integration_uri=$(echo "$method_json" | jq -r '.methodIntegration.uri // ""')
                            auth_type=$(echo "$method_json" | jq -r '.authorizationType // "NONE"')
                            
                            # Extract Lambda function name
                            lambda_name=""
                            if [[ "$integration_uri" =~ function:([^:/]+) ]]; then
                                lambda_name="${BASH_REMATCH[1]}"
                            fi
                            
                            if [ -n "$lambda_name" ]; then
                                cat >> "$OUTPUT_FILE" << EOF
        ${var_name}.add_method(
            "${method}",
            apigateway.LambdaIntegration(
                self.lambda_functions.get('${lambda_name}'),
                proxy=True
            ),
            authorization_type=apigateway.AuthorizationType.${auth_type}
        )
EOF
                            fi
                        fi
                    fi
                done
            fi
        done
    fi
    
    echo "" >> "$OUTPUT_FILE"
done

# Create WebSocket APIs section
cat >> "$OUTPUT_FILE" << 'EOF'
    
    def create_websocket_apis(self):
        """Create all WebSocket APIs with complete configuration"""
        
EOF

# Extract WebSocket APIs
echo "Extracting WebSocket APIs..."
websocket_apis_json=$(aws apigatewayv2 get-apis $AWS_OPTS)

# Filter for WebSocket APIs only
websocket_count=$(echo "$websocket_apis_json" | jq -r '[.Items[] | select(.ProtocolType=="WEBSOCKET")] | length')
echo "Found $websocket_count WebSocket APIs"

# Process each WebSocket API
for i in $(seq 0 $((websocket_count - 1))); do
    api_data=$(echo "$websocket_apis_json" | jq -r "[.Items[] | select(.ProtocolType==\"WEBSOCKET\")][$i]")
    api_id=$(echo "$api_data" | jq -r '.ApiId')
    api_name=$(echo "$api_data" | jq -r '.Name')
    api_description=$(echo "$api_data" | jq -r '.Description // ""' | sed 's/"/\\"/g')
    
    echo "Processing WebSocket API: $api_name ($api_id)"
    
    # Clean API name for variable use
    api_var_name=$(clean_var_name "$api_name")
    
    # Get stages
    stages_json=$(aws apigatewayv2 get-stages $AWS_OPTS --api-id "$api_id")
    stage_name=$(echo "$stages_json" | jq -r '.Items[0].StageName // "prod"')
    
    # Determine default Lambda function
    default_lambda=""
    case "$api_name" in
        "ReferralChatbotWebSocket")
            default_lambda="referralChatbotLambda"
            ;;
        "ProcessUserWebSocketAPI"|"UserFeedbackWebSocketAPI")
            default_lambda="ProcessUserData"
            ;;
        "AnalyticsWebSocketAPI")
            default_lambda="query-analytics-api"
            ;;
        "ReferralsWebSocketAPI")
            default_lambda="ReferralsApiHandler"
            ;;
    esac
    
    # Generate CDK code for this API
    cat >> "$OUTPUT_FILE" << EOF
        # ${api_name} - Original ID: ${api_id}
        ${api_var_name}_api = apigatewayv2.WebSocketApi(
            self.scope, "${api_name}",
            api_name="${api_name}",
            description="${api_description}",
        )
        
        ${api_var_name}_stage = apigatewayv2.WebSocketStage(
            self.scope, "${api_name}Stage",
            web_socket_api=${api_var_name}_api,
            stage_name="${stage_name}",
            auto_deploy=True
        )
        self.websocket_apis['${api_name}'] = (${api_var_name}_api, ${api_var_name}_stage)
        
        # Lambda integration
        ${api_var_name}_integration = integrations.WebSocketLambdaIntegration(
            "${api_name}Integration",
            handler=self.lambda_functions.get('${default_lambda}')
        )
        
EOF

    # Get routes
    routes_json=$(aws apigatewayv2 get-routes $AWS_OPTS --api-id "$api_id")
    if echo "$routes_json" | jq -e . >/dev/null 2>&1; then
        route_count=$(echo "$routes_json" | jq -r '.Items | length')
        
        for j in $(seq 0 $((route_count - 1))); do
            route_key=$(echo "$routes_json" | jq -r ".Items[$j].RouteKey")
            
            cat >> "$OUTPUT_FILE" << EOF
        # Route: ${route_key}
        ${api_var_name}_api.add_route(
            "${route_key}",
            integration=${api_var_name}_integration
        )
        
EOF
        done
    fi
    
    echo "" >> "$OUTPUT_FILE"
done

# Add the rest of the class
cat >> "$OUTPUT_FILE" << 'EOF'
    
    def create_outputs(self):
        """Create CloudFormation outputs for all APIs"""
        
        # REST API outputs
        for api_name, api in self.rest_apis.items():
            CfnOutput(self.scope, f"{api_name}Url",
                value=f"https://{api.rest_api_id}.execute-api.{self.scope.region}.amazonaws.com/{api.deployment_stage.stage_name}/",
                description=f"URL of the {api_name} REST API"
            )
        
        # WebSocket API outputs
        for api_name, (api, stage) in self.websocket_apis.items():
            CfnOutput(self.scope, f"{api_name}Url",
                value=f"wss://{api.api_id}.execute-api.{self.scope.region}.amazonaws.com/{stage.stage_name}/",
                description=f"URL of the {api_name} WebSocket API"
            )
    
    def add_lambda_permissions(self):
        """Add Lambda permissions for API Gateway invocations"""
        
        # REST API permissions
        for api_name, api in self.rest_apis.items():
            for lambda_name, lambda_fn in self.lambda_functions.items():
                lambda_fn.add_permission(
                    f"Allow{api_name}Invoke{lambda_name}",
                    principal=iam.ServicePrincipal("apigateway.amazonaws.com"),
                    action="lambda:InvokeFunction",
                    source_arn=f"arn:aws:execute-api:{self.scope.region}:{self.account_id}:{api.rest_api_id}/*/*"
                )
        
        # WebSocket API permissions
        for api_name, (api, stage) in self.websocket_apis.items():
            for lambda_name, lambda_fn in self.lambda_functions.items():
                lambda_fn.add_permission(
                    f"Allow{api_name}WebSocketInvoke{lambda_name}",
                    principal=iam.ServicePrincipal("apigateway.amazonaws.com"),
                    action="lambda:InvokeFunction",
                    source_arn=f"arn:aws:execute-api:{self.scope.region}:{self.account_id}:{api.api_id}/*/*/*"
                )


# Usage in your BrightpointStack:
# api_config = ApiGatewayComplete(self, self.account)
EOF

echo "Complete API Gateway configuration has been generated in: $OUTPUT_FILE"
echo "Add the generated code to your brightpoint_stack.py"