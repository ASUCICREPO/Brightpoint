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
        
        # UserDashboardAPI - Original ID: 329yd7xxm0
        UserDashboardAPI_api = apigateway.RestApi(
            self.scope, "UserDashboardAPI",
            rest_api_name="UserDashboardAPI",
            description="",
            deploy_options=apigateway.StageOptions(
                stage_name="dev",
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
        self.rest_apis['UserDashboardAPI'] = UserDashboardAPI_api
        
        # Resource: /dashboard
        UserDashboardAPI__dashboard = UserDashboardAPI_api.root.add_resource("dashboard")
        UserDashboardAPI__dashboard.add_method(
            "GET",
            apigateway.LambdaIntegration(
                self.lambda_functions.get('user-dashboard-data-processor'),
                proxy=True
            ),
            authorization_type=apigateway.AuthorizationType.NONE
        )

        # QueryAnalyticsAPI - Original ID: adt0bzrd3e
        QueryAnalyticsAPI_api = apigateway.RestApi(
            self.scope, "QueryAnalyticsAPI",
            rest_api_name="QueryAnalyticsAPI",
            description="",
            deploy_options=apigateway.StageOptions(
                stage_name="dev",
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
        self.rest_apis['QueryAnalyticsAPI'] = QueryAnalyticsAPI_api
        
        # Resource: /analytics
        QueryAnalyticsAPI__analytics = QueryAnalyticsAPI_api.root.add_resource("analytics")
        # Resource: /analytics/all
        QueryAnalyticsAPI__analytics_all = QueryAnalyticsAPI__analytics.add_resource("all")
        QueryAnalyticsAPI__analytics_all.add_method(
            "POST",
            apigateway.LambdaIntegration(
                self.lambda_functions.get('query-analytics-api'),
                proxy=True
            ),
            authorization_type=apigateway.AuthorizationType.NONE
        )

        # QueryAnalyticsAPI - Original ID: ite99ljw0b
        QueryAnalyticsAPI_api = apigateway.RestApi(
            self.scope, "QueryAnalyticsAPI",
            rest_api_name="QueryAnalyticsAPI",
            description="",
            deploy_options=apigateway.StageOptions(
                stage_name="dev",
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
        self.rest_apis['QueryAnalyticsAPI'] = QueryAnalyticsAPI_api
        
        # Resource: /analytics
        QueryAnalyticsAPI__analytics = QueryAnalyticsAPI_api.root.add_resource("analytics")
        # Resource: /analytics/queries
        QueryAnalyticsAPI__analytics_queries = QueryAnalyticsAPI__analytics.add_resource("queries")
        QueryAnalyticsAPI__analytics_queries.add_method(
            "POST",
            apigateway.LambdaIntegration(
                self.lambda_functions.get('query-analytics-api'),
                proxy=True
            ),
            authorization_type=apigateway.AuthorizationType.NONE
        )

        # createUser - Original ID: kahgke45yd
        createUser_api = apigateway.RestApi(
            self.scope, "createUser",
            rest_api_name="createUser",
            description="",
            deploy_options=apigateway.StageOptions(
                stage_name="dev",
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
        self.rest_apis['createUser'] = createUser_api
        
        # Resource: /addUser
        createUser__addUser = createUser_api.root.add_resource("addUser")
        createUser__addUser.add_method(
            "POST",
            apigateway.LambdaIntegration(
                self.lambda_functions.get('ProcessUserData'),
                proxy=True
            ),
            authorization_type=apigateway.AuthorizationType.NONE
        )

        # ReferralChatbotAPI - Original ID: pncxzrq0r9
        ReferralChatbotAPI_api = apigateway.RestApi(
            self.scope, "ReferralChatbotAPI",
            rest_api_name="ReferralChatbotAPI",
            description="",
            deploy_options=apigateway.StageOptions(
                stage_name="dev",
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
        self.rest_apis['ReferralChatbotAPI'] = ReferralChatbotAPI_api
        
        # Resource: /chat
        ReferralChatbotAPI__chat = ReferralChatbotAPI_api.root.add_resource("chat")
        ReferralChatbotAPI__chat.add_method(
            "POST",
            apigateway.LambdaIntegration(
                self.lambda_functions.get('referralChatbotLambda'),
                proxy=True
            ),
            authorization_type=apigateway.AuthorizationType.NONE
        )

        # ReferralsApi - Original ID: twi9ghqfhl
        ReferralsApi_api = apigateway.RestApi(
            self.scope, "ReferralsApi",
            rest_api_name="ReferralsApi",
            description="",
            deploy_options=apigateway.StageOptions(
                stage_name="dev",
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
        self.rest_apis['ReferralsApi'] = ReferralsApi_api
        
        # Resource: /referrals/{referral_id}
        ReferralsApi__referrals__referral_id_ = ReferralsApi__referrals.add_resource({referral_id})
        ReferralsApi__referrals__referral_id_.add_method(
            "DELETE",
            apigateway.LambdaIntegration(
                self.lambda_functions.get('ReferralsApiHandler'),
                proxy=True
            ),
            authorization_type=apigateway.AuthorizationType.NONE
        )
        ReferralsApi__referrals__referral_id_.add_method(
            "GET",
            apigateway.LambdaIntegration(
                self.lambda_functions.get('ReferralsApiHandler'),
                proxy=True
            ),
            authorization_type=apigateway.AuthorizationType.NONE
        )
        ReferralsApi__referrals__referral_id_.add_method(
            "POST",
            apigateway.LambdaIntegration(
                self.lambda_functions.get('ReferralsApiHandler'),
                proxy=True
            ),
            authorization_type=apigateway.AuthorizationType.NONE
        )
        ReferralsApi__referrals__referral_id_.add_method(
            "PUT",
            apigateway.LambdaIntegration(
                self.lambda_functions.get('ReferralsApiHandler'),
                proxy=True
            ),
            authorization_type=apigateway.AuthorizationType.NONE
        )
        # Resource: /referrals/search
        ReferralsApi__referrals_search = ReferralsApi__referrals.add_resource("search")
        ReferralsApi__referrals_search.add_method(
            "POST",
            apigateway.LambdaIntegration(
                self.lambda_functions.get('ReferralsApiHandler'),
                proxy=True
            ),
            authorization_type=apigateway.AuthorizationType.NONE
        )
        # Resource: /referrals
        ReferralsApi__referrals = ReferralsApi_api.root.add_resource("referrals")
        ReferralsApi__referrals.add_method(
            "DELETE",
            apigateway.LambdaIntegration(
                self.lambda_functions.get('ReferralsApiHandler'),
                proxy=True
            ),
            authorization_type=apigateway.AuthorizationType.NONE
        )
        ReferralsApi__referrals.add_method(
            "GET",
            apigateway.LambdaIntegration(
                self.lambda_functions.get('ReferralsApiHandler'),
                proxy=True
            ),
            authorization_type=apigateway.AuthorizationType.NONE
        )
        ReferralsApi__referrals.add_method(
            "POST",
            apigateway.LambdaIntegration(
                self.lambda_functions.get('ReferralsApiHandler'),
                proxy=True
            ),
            authorization_type=apigateway.AuthorizationType.NONE
        )
        ReferralsApi__referrals.add_method(
            "PUT",
            apigateway.LambdaIntegration(
                self.lambda_functions.get('ReferralsApiHandler'),
                proxy=True
            ),
            authorization_type=apigateway.AuthorizationType.NONE
        )

    
    def create_websocket_apis(self):
        """Create all WebSocket APIs with complete configuration"""
        
        # AnalyticsWebSocketAPI - Original ID: duqhouj11e
        AnalyticsWebSocketAPI_api = apigatewayv2.WebSocketApi(
            self.scope, "AnalyticsWebSocketAPI",
            api_name="AnalyticsWebSocketAPI",
            description="",
        )
        
        AnalyticsWebSocketAPI_stage = apigatewayv2.WebSocketStage(
            self.scope, "AnalyticsWebSocketAPIStage",
            web_socket_api=AnalyticsWebSocketAPI_api,
            stage_name="dev",
            auto_deploy=True
        )
        self.websocket_apis['AnalyticsWebSocketAPI'] = (AnalyticsWebSocketAPI_api, AnalyticsWebSocketAPI_stage)
        
        # Lambda integration
        AnalyticsWebSocketAPI_integration = integrations.WebSocketLambdaIntegration(
            "AnalyticsWebSocketAPIIntegration",
            handler=self.lambda_functions.get('query-analytics-api')
        )
        
        # Route: $default
        AnalyticsWebSocketAPI_api.add_route(
            "$default",
            integration=AnalyticsWebSocketAPI_integration
        )
        
        # Route: $connect
        AnalyticsWebSocketAPI_api.add_route(
            "$connect",
            integration=AnalyticsWebSocketAPI_integration
        )
        
        # Route: getAnalytics
        AnalyticsWebSocketAPI_api.add_route(
            "getAnalytics",
            integration=AnalyticsWebSocketAPI_integration
        )
        
        # Route: $disconnect
        AnalyticsWebSocketAPI_api.add_route(
            "$disconnect",
            integration=AnalyticsWebSocketAPI_integration
        )
        

        # ReferralChatbotWebSocket - Original ID: lajngh4a22
        ReferralChatbotWebSocket_api = apigatewayv2.WebSocketApi(
            self.scope, "ReferralChatbotWebSocket",
            api_name="ReferralChatbotWebSocket",
            description="",
        )
        
        ReferralChatbotWebSocket_stage = apigatewayv2.WebSocketStage(
            self.scope, "ReferralChatbotWebSocketStage",
            web_socket_api=ReferralChatbotWebSocket_api,
            stage_name="dev",
            auto_deploy=True
        )
        self.websocket_apis['ReferralChatbotWebSocket'] = (ReferralChatbotWebSocket_api, ReferralChatbotWebSocket_stage)
        
        # Lambda integration
        ReferralChatbotWebSocket_integration = integrations.WebSocketLambdaIntegration(
            "ReferralChatbotWebSocketIntegration",
            handler=self.lambda_functions.get('referralChatbotLambda')
        )
        
        # Route: $connect
        ReferralChatbotWebSocket_api.add_route(
            "$connect",
            integration=ReferralChatbotWebSocket_integration
        )
        
        # Route: query
        ReferralChatbotWebSocket_api.add_route(
            "query",
            integration=ReferralChatbotWebSocket_integration
        )
        
        # Route: $disconnect
        ReferralChatbotWebSocket_api.add_route(
            "$disconnect",
            integration=ReferralChatbotWebSocket_integration
        )
        

        # UserFeedbackWebSocketAPI - Original ID: p8ea1v23i0
        UserFeedbackWebSocketAPI_api = apigatewayv2.WebSocketApi(
            self.scope, "UserFeedbackWebSocketAPI",
            api_name="UserFeedbackWebSocketAPI",
            description="",
        )
        
        UserFeedbackWebSocketAPI_stage = apigatewayv2.WebSocketStage(
            self.scope, "UserFeedbackWebSocketAPIStage",
            web_socket_api=UserFeedbackWebSocketAPI_api,
            stage_name="dev",
            auto_deploy=True
        )
        self.websocket_apis['UserFeedbackWebSocketAPI'] = (UserFeedbackWebSocketAPI_api, UserFeedbackWebSocketAPI_stage)
        
        # Lambda integration
        UserFeedbackWebSocketAPI_integration = integrations.WebSocketLambdaIntegration(
            "UserFeedbackWebSocketAPIIntegration",
            handler=self.lambda_functions.get('ProcessUserData')
        )
        
        # Route: $disconnect
        UserFeedbackWebSocketAPI_api.add_route(
            "$disconnect",
            integration=UserFeedbackWebSocketAPI_integration
        )
        
        # Route: sendFeedback
        UserFeedbackWebSocketAPI_api.add_route(
            "sendFeedback",
            integration=UserFeedbackWebSocketAPI_integration
        )
        
        # Route: updateUser
        UserFeedbackWebSocketAPI_api.add_route(
            "updateUser",
            integration=UserFeedbackWebSocketAPI_integration
        )
        
        # Route: getUser
        UserFeedbackWebSocketAPI_api.add_route(
            "getUser",
            integration=UserFeedbackWebSocketAPI_integration
        )
        
        # Route: $connect
        UserFeedbackWebSocketAPI_api.add_route(
            "$connect",
            integration=UserFeedbackWebSocketAPI_integration
        )
        

        # ReferralsWebSocketAPI - Original ID: z0ebrmmyd0
        ReferralsWebSocketAPI_api = apigatewayv2.WebSocketApi(
            self.scope, "ReferralsWebSocketAPI",
            api_name="ReferralsWebSocketAPI",
            description="",
        )
        
        ReferralsWebSocketAPI_stage = apigatewayv2.WebSocketStage(
            self.scope, "ReferralsWebSocketAPIStage",
            web_socket_api=ReferralsWebSocketAPI_api,
            stage_name="dev",
            auto_deploy=True
        )
        self.websocket_apis['ReferralsWebSocketAPI'] = (ReferralsWebSocketAPI_api, ReferralsWebSocketAPI_stage)
        
        # Lambda integration
        ReferralsWebSocketAPI_integration = integrations.WebSocketLambdaIntegration(
            "ReferralsWebSocketAPIIntegration",
            handler=self.lambda_functions.get('ReferralsApiHandler')
        )
        
        # Route: getReferrals
        ReferralsWebSocketAPI_api.add_route(
            "getReferrals",
            integration=ReferralsWebSocketAPI_integration
        )
        
        # Route: $connect
        ReferralsWebSocketAPI_api.add_route(
            "$connect",
            integration=ReferralsWebSocketAPI_integration
        )
        
        # Route: createReferral
        ReferralsWebSocketAPI_api.add_route(
            "createReferral",
            integration=ReferralsWebSocketAPI_integration
        )
        
        # Route: searchReferrals
        ReferralsWebSocketAPI_api.add_route(
            "searchReferrals",
            integration=ReferralsWebSocketAPI_integration
        )
        
        # Route: $default
        ReferralsWebSocketAPI_api.add_route(
            "$default",
            integration=ReferralsWebSocketAPI_integration
        )
        
        # Route: updateReferral
        ReferralsWebSocketAPI_api.add_route(
            "updateReferral",
            integration=ReferralsWebSocketAPI_integration
        )
        
        # Route: $disconnect
        ReferralsWebSocketAPI_api.add_route(
            "$disconnect",
            integration=ReferralsWebSocketAPI_integration
        )
        
        # Route: deleteReferral
        ReferralsWebSocketAPI_api.add_route(
            "deleteReferral",
            integration=ReferralsWebSocketAPI_integration
        )
        
        # Route: getReferral
        ReferralsWebSocketAPI_api.add_route(
            "getReferral",
            integration=ReferralsWebSocketAPI_integration
        )
        

    
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
