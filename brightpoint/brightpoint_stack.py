from aws_cdk import (
    Stack,
    aws_lambda as lambda_,
    aws_dynamodb as dynamodb,
    aws_apigateway as apigateway,
    aws_iam as iam,
    CfnOutput,
    RemovalPolicy,
    Duration,
    aws_amplify_alpha as amplify,
    aws_cognito as cognito,
    aws_s3_assets as s3_assets,
    aws_apigatewayv2 as apigatewayv2,
    aws_apigatewayv2_integrations as integrations,
    Tags,
    SecretValue,
    aws_secretsmanager as secretsmanager,
    aws_codebuild as codebuild,
    RemovalPolicy,
)
from constructs import Construct
import os
from .config import EnvironmentConfig
from aws_cdk.aws_amplify_alpha import App, GitHubSourceCodeProvider
import json
from aws_cdk import aws_secretsmanager as secretsmanager


class ApiGatewayComplete:
    """Complete API Gateway configuration for BrightpointStack"""

    def __init__(self, scope: Stack, account_id: str, lambda_functions: dict, env_name: str):
        self.scope = scope
        self.account_id = account_id
        self.lambda_functions = lambda_functions
        self.env_name = env_name

        # Get environment-specific configuration
        self.config = EnvironmentConfig.get_config(env_name)

        # Store API references
        self.rest_apis = {}
        self.websocket_apis = {}

        # Create all APIs
        self.create_all_apis()

    def create_all_apis(self):
        """Create all REST and WebSocket APIs"""
        self.create_rest_apis()
        self.create_websocket_apis()
        # self.create_outputs()

    def create_rest_apis(self):
        """Create all REST APIs with complete configuration"""

        # UserDashboardAPI - Original ID: 329yd7xxm0
        UserDashboardAPI_api = apigateway.RestApi(
            self.scope, "UserDashboardAPI",
            rest_api_name=f"UserDashboardAPI-{self.env_name}",
            description=f"User Dashboard API - {self.env_name}",
            deploy_options=apigateway.StageOptions(
                stage_name=self.env_name,
                logging_level=self.config['api_settings']['logging_level'],
                data_trace_enabled=self.config['api_settings']['data_trace_enabled'],
                metrics_enabled=self.config['api_settings']['metrics_enabled']
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
                self.lambda_functions.get('ProcessUserData'),
                proxy=True
            ),
            authorization_type=apigateway.AuthorizationType.NONE
        )

        # QueryAnalyticsAPI1 - Original ID: adt0bzrd3e
        QueryAnalyticsAPI1_api = apigateway.RestApi(
            self.scope, "QueryAnalyticsAPI1",
            rest_api_name=f"QueryAnalyticsAPI-All-{self.env_name}",
            description=f"Query Analytics API - All - {self.env_name}",
            deploy_options=apigateway.StageOptions(
                stage_name=self.env_name,
                logging_level=self.config['api_settings']['logging_level'],
                data_trace_enabled=self.config['api_settings']['data_trace_enabled'],
                metrics_enabled=self.config['api_settings']['metrics_enabled']
            ),
            default_cors_preflight_options=apigateway.CorsOptions(
                allow_origins=apigateway.Cors.ALL_ORIGINS,
                allow_methods=apigateway.Cors.ALL_METHODS,
                allow_headers=["Content-Type", "X-Amz-Date", "Authorization", "X-Api-Key"]
            )
        )
        self.rest_apis['QueryAnalyticsAPI1'] = QueryAnalyticsAPI1_api

        # Resource: /analytics
        QueryAnalyticsAPI1__analytics = QueryAnalyticsAPI1_api.root.add_resource("analytics")
        # Resource: /analytics/all
        QueryAnalyticsAPI1__analytics_all = QueryAnalyticsAPI1__analytics.add_resource("all")
        QueryAnalyticsAPI1__analytics_all.add_method(
            "POST",
            apigateway.LambdaIntegration(
                self.lambda_functions.get('query-analytics-api'),
                proxy=True
            ),
            authorization_type=apigateway.AuthorizationType.NONE
        )

        # QueryAnalyticsAPI2 - Original ID: ite99ljw0b
        QueryAnalyticsAPI2_api = apigateway.RestApi(
            self.scope, "QueryAnalyticsAPI2",
            rest_api_name=f"QueryAnalyticsAPI-Queries-{self.env_name}",
            description=f"Query Analytics API - Queries - {self.env_name}",
            deploy_options=apigateway.StageOptions(
                stage_name=self.env_name,
                logging_level=self.config['api_settings']['logging_level'],
                data_trace_enabled=self.config['api_settings']['data_trace_enabled'],
                metrics_enabled=self.config['api_settings']['metrics_enabled']
            ),
            default_cors_preflight_options=apigateway.CorsOptions(
                allow_origins=apigateway.Cors.ALL_ORIGINS,
                allow_methods=apigateway.Cors.ALL_METHODS,
                allow_headers=["Content-Type", "X-Amz-Date", "Authorization", "X-Api-Key"]
            )
        )
        self.rest_apis['QueryAnalyticsAPI2'] = QueryAnalyticsAPI2_api

        # Resource: /analytics
        QueryAnalyticsAPI2__analytics = QueryAnalyticsAPI2_api.root.add_resource("analytics")
        # Resource: /analytics/queries
        QueryAnalyticsAPI2__analytics_queries = QueryAnalyticsAPI2__analytics.add_resource("queries")
        QueryAnalyticsAPI2__analytics_queries.add_method(
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
            rest_api_name=f"createUser-{self.env_name}",
            description=f"Create User API - {self.env_name}",
            deploy_options=apigateway.StageOptions(
                stage_name=self.env_name,
                logging_level=self.config['api_settings']['logging_level'],
                data_trace_enabled=self.config['api_settings']['data_trace_enabled'],
                metrics_enabled=self.config['api_settings']['metrics_enabled']
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
            "PUT",
            apigateway.LambdaIntegration(
                self.lambda_functions.get('ProcessUserData'),
                proxy=True
            ),
            authorization_type=apigateway.AuthorizationType.NONE
        )

        # ReferralChatbotAPI - Original ID: pncxzrq0r9
        ReferralChatbotAPI_api = apigateway.RestApi(
            self.scope, "ReferralChatbotAPI",
            rest_api_name=f"ReferralChatbotAPI-{self.env_name}",
            description=f"Referral Chatbot API - {self.env_name}",
            deploy_options=apigateway.StageOptions(
                stage_name=self.env_name,
                logging_level=self.config['api_settings']['logging_level'],
                data_trace_enabled=self.config['api_settings']['data_trace_enabled'],
                metrics_enabled=self.config['api_settings']['metrics_enabled']
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
            rest_api_name=f"ReferralsApi-{self.env_name}",
            description=f"Referrals API - {self.env_name}",
            deploy_options=apigateway.StageOptions(
                stage_name=self.env_name,
                logging_level=self.config['api_settings']['logging_level'],
                data_trace_enabled=self.config['api_settings']['data_trace_enabled'],
                metrics_enabled=self.config['api_settings']['metrics_enabled']
            ),
            default_cors_preflight_options=apigateway.CorsOptions(
                allow_origins=apigateway.Cors.ALL_ORIGINS,
                allow_methods=apigateway.Cors.ALL_METHODS,
                allow_headers=["Content-Type", "X-Amz-Date", "Authorization", "X-Api-Key"]
            )
        )
        self.rest_apis['ReferralsApi'] = ReferralsApi_api

        # Resource: /referrals
        ReferralsApi__referrals = ReferralsApi_api.root.add_resource("referrals")

        # Add methods to /referrals
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

        # Resource: /referrals/{referral_id}
        ReferralsApi__referrals__referral_id_ = ReferralsApi__referrals.add_resource("{referral_id}")
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

    def create_websocket_apis(self):
        """Create all WebSocket APIs with complete configuration"""

        # AnalyticsWebSocketAPI - Original ID: duqhouj11e
        AnalyticsWebSocketAPI_api = apigatewayv2.WebSocketApi(
            self.scope, "AnalyticsWebSocketAPI",
            api_name=f"AnalyticsWebSocketAPI-{self.env_name}",
            description=f"Analytics WebSocket API - {self.env_name}",
        )

        AnalyticsWebSocketAPI_stage = apigatewayv2.WebSocketStage(
            self.scope, "AnalyticsWebSocketAPIStage",
            web_socket_api=AnalyticsWebSocketAPI_api,
            stage_name=self.env_name,
            auto_deploy=True
        )
        self.websocket_apis['AnalyticsWebSocketAPI'] = (AnalyticsWebSocketAPI_api, AnalyticsWebSocketAPI_stage)

        # Lambda integration
        AnalyticsWebSocketAPI_integration = integrations.WebSocketLambdaIntegration(
            "AnalyticsWebSocketAPIIntegration",
            handler=self.lambda_functions.get('query-analytics-api')
        )

        # Routes
        AnalyticsWebSocketAPI_api.add_route(
            "$default",
            integration=AnalyticsWebSocketAPI_integration
        )
        AnalyticsWebSocketAPI_api.add_route(
            "$connect",
            integration=AnalyticsWebSocketAPI_integration
        )
        AnalyticsWebSocketAPI_api.add_route(
            "getAnalytics",
            integration=AnalyticsWebSocketAPI_integration
        )
        AnalyticsWebSocketAPI_api.add_route(
            "$disconnect",
            integration=AnalyticsWebSocketAPI_integration
        )

        # ReferralChatbotWebSocket - Original ID: lajngh4a22
        ReferralChatbotWebSocket_api = apigatewayv2.WebSocketApi(
            self.scope, "ReferralChatbotWebSocket",
            api_name=f"ReferralChatbotWebSocket-{self.env_name}",
            description=f"Referral Chatbot WebSocket API - {self.env_name}",
        )

        ReferralChatbotWebSocket_stage = apigatewayv2.WebSocketStage(
            self.scope, "ReferralChatbotWebSocketStage",
            web_socket_api=ReferralChatbotWebSocket_api,
            stage_name=self.env_name,
            auto_deploy=True
        )
        self.websocket_apis['ReferralChatbotWebSocket'] = (ReferralChatbotWebSocket_api, ReferralChatbotWebSocket_stage)

        # Lambda integration
        ReferralChatbotWebSocket_integration = integrations.WebSocketLambdaIntegration(
            "ReferralChatbotWebSocketIntegration",
            handler=self.lambda_functions.get('referralChatbotLambda')
        )

        # Routes
        ReferralChatbotWebSocket_api.add_route(
            "$connect",
            integration=ReferralChatbotWebSocket_integration
        )
        ReferralChatbotWebSocket_api.add_route(
            "query",
            integration=ReferralChatbotWebSocket_integration
        )
        ReferralChatbotWebSocket_api.add_route(
            "$disconnect",
            integration=ReferralChatbotWebSocket_integration
        )

        # UserFeedbackWebSocketAPI - Original ID: p8ea1v23i0
        UserFeedbackWebSocketAPI_api = apigatewayv2.WebSocketApi(
            self.scope, "UserFeedbackWebSocketAPI",
            api_name=f"UserFeedbackWebSocketAPI-{self.env_name}",
            description=f"User Feedback WebSocket API - {self.env_name}",
        )

        UserFeedbackWebSocketAPI_stage = apigatewayv2.WebSocketStage(
            self.scope, "UserFeedbackWebSocketAPIStage",
            web_socket_api=UserFeedbackWebSocketAPI_api,
            stage_name=self.env_name,
            auto_deploy=True
        )
        self.websocket_apis['UserFeedbackWebSocketAPI'] = (UserFeedbackWebSocketAPI_api, UserFeedbackWebSocketAPI_stage)

        # Lambda integration
        UserFeedbackWebSocketAPI_integration = integrations.WebSocketLambdaIntegration(
            "UserFeedbackWebSocketAPIIntegration",
            handler=self.lambda_functions.get('ProcessUserData')
        )

        # Routes
        UserFeedbackWebSocketAPI_api.add_route(
            "$disconnect",
            integration=UserFeedbackWebSocketAPI_integration
        )
        UserFeedbackWebSocketAPI_api.add_route(
            "sendFeedback",
            integration=UserFeedbackWebSocketAPI_integration
        )
        UserFeedbackWebSocketAPI_api.add_route(
            "updateUser",
            integration=UserFeedbackWebSocketAPI_integration
        )
        UserFeedbackWebSocketAPI_api.add_route(
            "getUser",
            integration=UserFeedbackWebSocketAPI_integration
        )
        UserFeedbackWebSocketAPI_api.add_route(
            "$connect",
            integration=UserFeedbackWebSocketAPI_integration
        )

        # ReferralsWebSocketAPI - Original ID: z0ebrmmyd0
        ReferralsWebSocketAPI_api = apigatewayv2.WebSocketApi(
            self.scope, "ReferralsWebSocketAPI",
            api_name=f"ReferralsWebSocketAPI-{self.env_name}",
            description=f"Referrals WebSocket API - {self.env_name}",
        )

        ReferralsWebSocketAPI_stage = apigatewayv2.WebSocketStage(
            self.scope, "ReferralsWebSocketAPIStage",
            web_socket_api=ReferralsWebSocketAPI_api,
            stage_name=self.env_name,
            auto_deploy=True
        )
        self.websocket_apis['ReferralsWebSocketAPI'] = (ReferralsWebSocketAPI_api, ReferralsWebSocketAPI_stage)

        # Lambda integration
        ReferralsWebSocketAPI_integration = integrations.WebSocketLambdaIntegration(
            "ReferralsWebSocketAPIIntegration",
            handler=self.lambda_functions.get('ReferralsApiHandler')
        )

        # Routes
        ReferralsWebSocketAPI_api.add_route(
            "getReferrals",
            integration=ReferralsWebSocketAPI_integration
        )
        ReferralsWebSocketAPI_api.add_route(
            "$connect",
            integration=ReferralsWebSocketAPI_integration
        )
        ReferralsWebSocketAPI_api.add_route(
            "createReferral",
            integration=ReferralsWebSocketAPI_integration
        )
        ReferralsWebSocketAPI_api.add_route(
            "searchReferrals",
            integration=ReferralsWebSocketAPI_integration
        )
        ReferralsWebSocketAPI_api.add_route(
            "$default",
            integration=ReferralsWebSocketAPI_integration
        )
        ReferralsWebSocketAPI_api.add_route(
            "updateReferral",
            integration=ReferralsWebSocketAPI_integration
        )
        ReferralsWebSocketAPI_api.add_route(
            "$disconnect",
            integration=ReferralsWebSocketAPI_integration
        )
        ReferralsWebSocketAPI_api.add_route(
            "deleteReferral",
            integration=ReferralsWebSocketAPI_integration
        )
        ReferralsWebSocketAPI_api.add_route(
            "getReferral",
            integration=ReferralsWebSocketAPI_integration
        )

    # def create_outputs(self):
    #     """Create CloudFormation outputs for all APIs"""

    #     # REST API outputs
    #     for api_name, api in self.rest_apis.items():
    #         CfnOutput(self.scope, f"{api_name}Url",
    #             value=f"https://{api.rest_api_id}.execute-api.{self.scope.region}.amazonaws.com/{api.deployment_stage.stage_name}/",
    #             description=f"URL of the {api_name} REST API"
    #         )

    #     # WebSocket API outputs
    #     for api_name, (api, stage) in self.websocket_apis.items():
    #         CfnOutput(self.scope, f"{api_name}Url",
    #             value=f"wss://{api.api_id}.execute-api.{self.scope.region}.amazonaws.com/{stage.stage_name}/",
    #             description=f"URL of the {api_name} WebSocket API"
    #         )


class BrightpointStack(Stack):

    def __init__(self, scope: Construct, construct_id: str, env_name: str = "dev", **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)

        # Get account_id and region from stack environment
        self.env_name = self.node.try_get_context("env")
        self.account_id = self.node.try_get_context("account")
        self.target_region = self.node.try_get_context("region")

        if not self.env_name:
            raise ValueError("Environment must be provided via -c env=<env_name>")
        if not self.account_id:
            raise ValueError("Account ID must be provided via -c account=<account_id>")
        if not self.target_region:
            raise ValueError("Region must be provided via -c region=<region>")

        perplexity_secret = secretsmanager.Secret.from_secret_name_v2(
            self, "PerplexityApiKeySecret",
            secret_name="perplexity_api_key"
        )

        # Get environment-specific configuration
        self.config = EnvironmentConfig.get_config(env_name)

        github_token_secret = secretsmanager.Secret.from_secret_name_v2(
            self, "GitHubTokenSecret", "github-token"
        )

        # Get the plaintext secret value
        github_token = github_token_secret.secret_value

        # Add tags to all resources in this stack
        Tags.of(self).add("Environment", self.env_name)
        Tags.of(self).add("Application", "Brightpoint")

        # DynamoDB Tables Creation with environment prefix
        # Table: WebSocketConnections
        websocket_connections_table = dynamodb.Table(
            self, 'WebSocketConnectionsTable',
            table_name=f'WebSocketConnections-{self.env_name}',
            partition_key=dynamodb.Attribute(name='connectionId', type=dynamodb.AttributeType.STRING),
            billing_mode=self.config['table_settings']['billing_mode'],
            removal_policy=self.config['table_settings']['removal_policy'],
        )

        # Table: perplexity_query_cache
        perplexity_query_cache_table = dynamodb.Table(
            self, 'perplexity_query_cacheTable',
            table_name=f'perplexity_query_cache-{self.env_name}',
            partition_key=dynamodb.Attribute(name='query_id', type=dynamodb.AttributeType.STRING),
            billing_mode=self.config['table_settings']['billing_mode'],
            removal_policy=self.config['table_settings']['removal_policy'],
        )

        # Table: query_analytics
        query_analytics_table = dynamodb.Table(
            self, 'query_analyticsTable',
            table_name=f'query_analytics-{self.env_name}',
            partition_key=dynamodb.Attribute(name='query_text', type=dynamodb.AttributeType.STRING),
            sort_key=dynamodb.Attribute(name='Zipcode', type=dynamodb.AttributeType.STRING),
            billing_mode=self.config['table_settings']['billing_mode'],
            removal_policy=self.config['table_settings']['removal_policy'],
        )

        # Table: referral_data
        referral_data_table = dynamodb.Table(
            self, 'referral_dataTable',
            table_name=f'referral_data-{self.env_name}',
            partition_key=dynamodb.Attribute(name='referral_id', type=dynamodb.AttributeType.STRING),
            billing_mode=self.config['table_settings']['billing_mode'],
            removal_policy=self.config['table_settings']['removal_policy'],
        )

        # Table: user_data
        user_data_table = dynamodb.Table(
            self, 'user_dataTable',
            table_name=f'user_data-{self.env_name}',
            partition_key=dynamodb.Attribute(name='user_id', type=dynamodb.AttributeType.STRING),
            billing_mode=self.config['table_settings']['billing_mode'],
            stream=dynamodb.StreamViewType.NEW_AND_OLD_IMAGES,
            removal_policy=self.config['table_settings']['removal_policy'],
        )

        # Global Secondary Index for user_data
        user_data_table.add_global_secondary_index(
            index_name='Phone-index',
            partition_key=dynamodb.Attribute(name='Phone', type=dynamodb.AttributeType.STRING),
            projection_type=dynamodb.ProjectionType.ALL,
        )

        # --- Cognito User Pool ---

        user_pool = cognito.UserPool(
            self, "BrightpointUserPool",
            user_pool_name=f"BrightpointUserPool-{self.env_name}",
            self_sign_up_enabled=True,
            sign_in_aliases=cognito.SignInAliases(
                username=True,
                email=True
            ),
            auto_verify=cognito.AutoVerifiedAttrs(email=True),
            standard_attributes=cognito.StandardAttributes(
                email=cognito.StandardAttribute(required=True, mutable=True)
            ),
            password_policy=cognito.PasswordPolicy(
                min_length=6,
                require_digits=False,
                require_lowercase=False,
                require_uppercase=False,
                require_symbols=False,
            ),
            account_recovery=cognito.AccountRecovery.EMAIL_ONLY,

            user_verification=cognito.UserVerificationConfig(
                email_subject="Verify your Brightpoint account",
                email_body="Welcome to Brightpoint! Your verification code is {####}",
                email_style=cognito.VerificationEmailStyle.CODE,
            )
        )

        user_pool_client = cognito.UserPoolClient(
            self, "BrightpointUserPoolClient",
            user_pool_client_name=f"BrightpointUserPoolClient-{self.env_name}",
            user_pool=user_pool,
            generate_secret=False,
            auth_flows=cognito.AuthFlow(
                user_password=True,
                user_srp=True,
                admin_user_password=True
            ),

            id_token_validity=Duration.hours(24),
            access_token_validity=Duration.hours(24),
            refresh_token_validity=Duration.days(30),

            o_auth=cognito.OAuthSettings(
                flows=cognito.OAuthFlows(
                    authorization_code_grant=True,
                    implicit_code_grant=True
                ),
                scopes=[cognito.OAuthScope.EMAIL, cognito.OAuthScope.OPENID, cognito.OAuthScope.PROFILE],
                callback_urls=[
                    f"https://frontend-code.{self.env_name}.amplifyapp.com/",
                    "http://localhost:3000/"  # For development
                ],
                logout_urls=[
                    f"https://frontend-code.{self.env_name}.amplifyapp.com/",
                    "http://localhost:3000/"  # For development
                ]
            )
        )

        user_pool_domain = cognito.UserPoolDomain(
            self, "BrightpointUserPoolDomain",
            user_pool=user_pool,
            cognito_domain=cognito.CognitoDomainOptions(
                domain_prefix=f"brightpoint-{self.env_name}"
            )
        )

        identity_pool = cognito.CfnIdentityPool(
            self, "BrightpointIdentityPool",
            identity_pool_name=f"BrightpointIdentityPool-{self.env_name}",
            allow_unauthenticated_identities=False,
            cognito_identity_providers=[{
                "clientId": user_pool_client.user_pool_client_id,
                "providerName": user_pool.user_pool_provider_name,
            }]
        )

        authenticated_role = iam.Role(
            self, "CognitoAuthenticatedRole",
            role_name=f"Cognito_BrightpointIdentityPool_AuthRole_{self.env_name}",
            assumed_by=iam.FederatedPrincipal(
                "cognito-identity.amazonaws.com",
                conditions={
                    "StringEquals": {
                        "cognito-identity.amazonaws.com:aud": identity_pool.ref
                    },
                    "ForAnyValue:StringLike": {
                        "cognito-identity.amazonaws.com:amr": "authenticated"
                    }
                },
                assume_role_action="sts:AssumeRoleWithWebIdentity"
            )
        )

        # Add basic permissions for authenticated users
        authenticated_role.add_to_policy(
            iam.PolicyStatement(
                effect=iam.Effect.ALLOW,
                actions=[
                    "mobileanalytics:PutEvents",
                    "cognito-sync:*",
                    "cognito-identity:*"
                ],
                resources=["*"]
            )
        )

        # Attach roles to identity pool
        cognito.CfnIdentityPoolRoleAttachment(
            self, "IdentityPoolRoleAttachment",
            identity_pool_id=identity_pool.ref,
            roles={
                "authenticated": authenticated_role.role_arn
            }
        )

        # --- Amplify Hosting ---
        amplify_app = amplify.App(
            self, "BrightpointManualAmplifyApp",
            app_name=f"brightpoint-{self.env_name}-app",
            description=f"Amplify App for manually deployed frontend - {self.env_name}",
            auto_branch_deletion=False
            # Note: No build_spec or source_code_provider needed for manual deployment
        )

        # Connect to frontend-code branch
        env_branch = amplify_app.add_branch("backend_code")

        env_branch.add_environment("REACT_APP_ENVIRONMENT", self.env_name)
        env_branch.add_environment("REACT_APP_USER_POOL_ID", user_pool.user_pool_id)
        env_branch.add_environment("REACT_APP_USER_POOL_CLIENT_ID", user_pool_client.user_pool_client_id)
        env_branch.add_environment("REACT_APP_IDENTITY_POOL_ID", identity_pool.ref)
        env_branch.add_environment("REACT_APP_REGION", self.target_region)
        env_branch.add_environment("REACT_APP_USER_POOL_DOMAIN", f"https://brightpoint-{self.env_name}.auth.{self.target_region}.amazoncognito.com")


        # Create Lambda execution roles with environment-specific names
        referral_chatbot_role = iam.Role(
            self, "ReferralChatbotRole",
            role_name=f"referralChatbotLambda-role-{self.env_name}",
            assumed_by=iam.ServicePrincipal("lambda.amazonaws.com"),
            description=f"Role for Brightpoint Referral Chatbot Lambda function - {self.env_name}"
        )
        self.add_referral_chatbot_role_policies(referral_chatbot_role, self.account_id)

        perplexity_lambda_role = iam.Role(
            self, "PerplexityLambdaRole",
            role_name=f"perplexityLambda-role-{self.env_name}",
            assumed_by=iam.ServicePrincipal("lambda.amazonaws.com"),
            description=f"Role for Perplexity Lambda function - {self.env_name}"
        )
        self.add_perplexity_lambda_role_policies(perplexity_lambda_role, self.account_id)

        process_user_data_role = iam.Role(
            self, "ProcessUserDataRole",
            role_name=f"LambdaUserDynamoDBRole-{self.env_name}",
            assumed_by=iam.ServicePrincipal("lambda.amazonaws.com"),
            description=f"Role for Process User Data Lambda function - {self.env_name}"
        )
        self.add_process_user_data_role_policies(process_user_data_role, self.account_id)

        query_analytics_backfill_role = iam.Role(
            self, "QueryAnalyticsBackfillRole",
            role_name=f"query-analytics-backfill-role-{self.env_name}",
            assumed_by=iam.ServicePrincipal("lambda.amazonaws.com"),
            description=f"Role for Query Analytics Backfill Lambda function - {self.env_name}"
        )
        self.add_query_analytics_backfill_role_policies(query_analytics_backfill_role, self.account_id)

        query_analytics_api_role = iam.Role(
            self, "QueryAnalyticsApiRole",
            role_name=f"query-analytics-api-role-{self.env_name}",
            assumed_by=iam.ServicePrincipal("lambda.amazonaws.com"),
            description=f"Role for Query Analytics API Lambda function - {self.env_name}"
        )
        self.add_query_analytics_api_role_policies(query_analytics_api_role, self.account_id)

        referrals_api_handler_role = iam.Role(
            self, "ReferralsApiHandlerRole",
            role_name=f"ReferralsApiHandler-role-{self.env_name}",
            assumed_by=iam.ServicePrincipal("lambda.amazonaws.com"),
            description=f"Role for Referrals API Handler Lambda function - {self.env_name}"
        )
        self.add_referrals_api_handler_role_policies(referrals_api_handler_role, self.account_id)

        sms_chat_integration_role = iam.Role(
            self, "SmsChatIntegrationRole",
            role_name=f"smsChatIntegration-role-{self.env_name}",
            assumed_by=iam.ServicePrincipal("lambda.amazonaws.com"),
            description=f"Role for SMS Chat Integration Lambda function - {self.env_name}"
        )
        self.add_sms_chat_integration_role_policies(sms_chat_integration_role, self.account_id)

        query_analytics_stream_processor_role = iam.Role(
            self, "QueryAnalyticsStreamProcessorRole",
            role_name=f"query-analytics-stream-processor-role-{self.env_name}",
            assumed_by=iam.ServicePrincipal("lambda.amazonaws.com"),
            description=f"Role for Query Analytics Stream Processor Lambda function - {self.env_name}"
        )
        self.add_query_analytics_stream_processor_role_policies(query_analytics_stream_processor_role, self.account_id)

        # Create Lambda functions with environment-specific names
        referral_chatbot_fn = lambda_.Function(
            self, "ReferralChatbotLambdaFn",
            function_name=f"referralChatbotLambda-{self.env_name}",
            runtime=lambda_.Runtime.PYTHON_3_12,
            code=lambda_.Code.from_asset("brightpoint/referral_chatbot"),
            handler="referralChatbotLambda.lambda_handler",
            role=referral_chatbot_role,
            timeout=Duration.seconds(self.config['timeout']['referralChatbotLambda']),
            memory_size=self.config['memory_size']['referralChatbotLambda'],
            architecture=lambda_.Architecture.X86_64,
            environment={
                "ENVIRONMENT": self.env_name,
                "REFERRAL_TABLE": f"referral_data-{self.env_name}",
                "USER_TABLE": f"user_data-{self.env_name}"
            }
        )

        perplexity_lambda_fn = lambda_.Function(
            self, "PerplexityLambdaFn",
            function_name=f"perplexityLambda-{self.env_name}",
            runtime=lambda_.Runtime.PYTHON_3_12,
            code=lambda_.Code.from_asset("brightpoint/perplexity_lambda"),
            handler="lambda_function.lambda_handler",
            role=perplexity_lambda_role,
            timeout=Duration.seconds(self.config['timeout']['perplexityLambda']),
            memory_size=self.config['memory_size']['perplexityLambda'],
            architecture=lambda_.Architecture.X86_64,
            environment={
                "ENVIRONMENT": self.env_name,
                "PERPLEXITY_API_KEY_SECRET_ARN": perplexity_secret.secret_arn,
                "CACHE_TABLE": f"perplexity_query_cache-{self.env_name}"
            }
        )

        perplexity_secret.grant_read(perplexity_lambda_fn)

        process_user_data_fn = lambda_.Function(
            self, "ProcessUserDataFn",
            function_name=f"ProcessUserData-{self.env_name}",
            runtime=lambda_.Runtime.PYTHON_3_12,
            code=lambda_.Code.from_asset("brightpoint/process_user_data"),
            handler="lambda_function.lambda_handler",
            role=process_user_data_role,
            timeout=Duration.seconds(self.config['timeout']['ProcessUserData']),
            memory_size=self.config['memory_size']['ProcessUserData'],
            architecture=lambda_.Architecture.X86_64,
            environment={
                "ENVIRONMENT": self.env_name,
                "USER_TABLE": f"user_data-{self.env_name}",
                "WEBSOCKET_TABLE": f"WebSocketConnections-{self.env_name}"
            }
        )

        query_analytics_api_fn = lambda_.Function(
            self, "QueryAnalyticsApiFn",
            function_name=f"query-analytics-api-{self.env_name}",
            runtime=lambda_.Runtime.PYTHON_3_12,
            code=lambda_.Code.from_asset("brightpoint/query_analytics_api"),
            handler="lambda_function.lambda_handler",
            role=query_analytics_api_role,
            timeout=Duration.seconds(self.config['timeout']['query-analytics-api']),
            memory_size=self.config['memory_size']['query-analytics-api'],
            architecture=lambda_.Architecture.X86_64,
            environment={
                "ENVIRONMENT": self.env_name,
                "ANALYTICS_TABLE": f"query_analytics-{self.env_name}"
            }
        )

        referrals_api_handler_fn = lambda_.Function(
            self, "ReferralsApiHandlerFn",
            function_name=f"ReferralsApiHandler-{self.env_name}",
            runtime=lambda_.Runtime.PYTHON_3_12,
            code=lambda_.Code.from_asset("brightpoint/referrals_api_handler"),
            handler="lambda_function.lambda_handler",
            role=referrals_api_handler_role,
            timeout=Duration.seconds(self.config['timeout']['ReferralsApiHandler']),
            memory_size=self.config['memory_size']['ReferralsApiHandler'],
            architecture=lambda_.Architecture.X86_64,
            environment={
                "ENVIRONMENT": self.env_name,
                "REFERRAL_TABLE": f"referral_data-{self.env_name}",
                "WEBSOCKET_TABLE": f"WebSocketConnections-{self.env_name}"
            }
        )

        query_analytics_backfill_fn = lambda_.Function(
            self, "QueryAnalyticsBackfillFn",
            function_name=f"query-analytics-backfill-{self.env_name}",
            runtime=lambda_.Runtime.PYTHON_3_12,
            code=lambda_.Code.from_asset("brightpoint/query_analytics_backfill"),
            handler="lambda_function.lambda_handler",
            role=query_analytics_backfill_role,
            timeout=Duration.seconds(900),
            memory_size=512,
            architecture=lambda_.Architecture.X86_64,
            environment={
                "ENVIRONMENT": self.env_name
            }
        )

        sms_chat_integration_fn = lambda_.Function(
            self, "SmsChatIntegrationFn",
            function_name=f"smsChatIntegration-{self.env_name}",
            runtime=lambda_.Runtime.PYTHON_3_12,
            code=lambda_.Code.from_asset("brightpoint/sms_chat_integration"),
            handler="lambda_function.lambda_handler",
            role=sms_chat_integration_role,
            timeout=Duration.seconds(300),
            memory_size=2048,
            architecture=lambda_.Architecture.X86_64,
            environment={
                "ENVIRONMENT": self.env_name,
                "USER_TABLE_NAME": f"user_data-{self.env_name}",
                "LOGIN_URL": "https://www.google.com/",
                "PINPOINT_APPLICATION_ID": "38a47a3f1a734353a4621a2cf90ada0c",
                "API_GATEWAY_URL": f"https://pncxzrq0r9.execute-api.us-east-1.amazonaws.com/{self.env_name}/chat",
                "HTTP_TIMEOUT": "60",
                "REGISTRATION_URL": "https://www.google.com/"
            }
        )

        # Add SNS trigger permission (cross-account)
        sms_chat_integration_fn.add_permission(
            "AllowSNSInvoke",
            principal=iam.ServicePrincipal("sns.amazonaws.com"),
            action="lambda:InvokeFunction",
            source_arn="arn:aws:sns:us-east-1:514811724234:PinpointV3Stack-responselambdatwoWaySMStopicC0D976B7-ntcREJoZGzuH"
        )

        query_analytics_stream_processor_fn = lambda_.Function(
            self, "QueryAnalyticsStreamProcessorFn",
            function_name=f"query-analytics-stream-processor-{self.env_name}",
            runtime=lambda_.Runtime.PYTHON_3_12,
            code=lambda_.Code.from_asset("brightpoint/query_analytics_stream_processor"),
            handler="lambda_function.lambda_handler",
            role=query_analytics_stream_processor_role,
            timeout=Duration.seconds(300),
            memory_size=512,
            architecture=lambda_.Architecture.X86_64,
            environment={
                "ENVIRONMENT": self.env_name
            }
        )

        # Add DynamoDB stream event source mapping
        query_analytics_stream_processor_fn.add_event_source_mapping(
            "UserDataStreamMapping",
            event_source_arn=user_data_table.table_stream_arn,
            starting_position=lambda_.StartingPosition.LATEST,
            batch_size=100,
            parallelization_factor=1,
            retry_attempts=0,
        )

        # Create dictionary of Lambda functions for API Gateway
        lambda_functions = {
            'referralChatbotLambda': referral_chatbot_fn,
            'perplexityLambda': perplexity_lambda_fn,
            'ProcessUserData': process_user_data_fn,
            'query-analytics-api': query_analytics_api_fn,
            'ReferralsApiHandler': referrals_api_handler_fn,
        }

        # Create API Gateway configuration
        api_config = ApiGatewayComplete(self, self.account_id, lambda_functions, self.env_name)

        env_branch.add_environment("REACT_APP_CHAT_API", f"wss://{api_config.websocket_apis['ReferralChatbotWebSocket'][0].api_id}.execute-api.{self.target_region}.amazonaws.com/{self.env_name}")
        env_branch.add_environment("REACT_APP_USER_API", f"wss://{api_config.websocket_apis['UserFeedbackWebSocketAPI'][0].api_id}.execute-api.{self.target_region}.amazonaws.com/{self.env_name}/")
        env_branch.add_environment("REACT_APP_REFERRAL_MANAGEMENT_API", f"wss://{api_config.websocket_apis['ReferralsWebSocketAPI'][0].api_id}.execute-api.{self.target_region}.amazonaws.com/{self.env_name}/")

        env_branch.add_environment("REACT_APP_ANALYTICS_API", f"https://{api_config.rest_apis['QueryAnalyticsAPI1'].rest_api_id}.execute-api.{self.target_region}.amazonaws.com/{self.env_name}/analytics/all")
        env_branch.add_environment("REACT_APP_USER_ADD_API", f"https://{api_config.rest_apis['createUser'].rest_api_id}.execute-api.{self.target_region}.amazonaws.com/{self.env_name}/")

        env_branch.add_environment("REACT_APP_REFERRAL_CHATBOT_REST_API", f"https://{api_config.rest_apis['ReferralChatbotAPI'].rest_api_id}.execute-api.{self.target_region}.amazonaws.com/{self.env_name}/chat")
        env_branch.add_environment("REACT_APP_REFERRALS_REST_API", f"https://{api_config.rest_apis['ReferralsApi'].rest_api_id}.execute-api.{self.target_region}.amazonaws.com/{self.env_name}/referrals")

        env_branch.add_environment("REACT_APP_CHAT_API_ID", api_config.websocket_apis['ReferralChatbotWebSocket'][0].api_id)
        env_branch.add_environment("REACT_APP_USER_API_ID", api_config.websocket_apis['UserFeedbackWebSocketAPI'][0].api_id)
        env_branch.add_environment("REACT_APP_REFERRAL_MANAGEMENT_API_ID", api_config.websocket_apis['ReferralsWebSocketAPI'][0].api_id)
        env_branch.add_environment("REACT_APP_ANALYTICS_API_ID", api_config.rest_apis['QueryAnalyticsAPI1'].rest_api_id)
        env_branch.add_environment("REACT_APP_CREATE_USER_API_ID", api_config.rest_apis['createUser'].rest_api_id)

        # Add Lambda permissions for API Gateway invocations
        # REST API permissions
        for api_name, api in api_config.rest_apis.items():
            if api_name == 'ReferralChatbotAPI':
                referral_chatbot_fn.add_permission(
                    "AllowReferralChatbotAPIInvoke",
                    principal=iam.ServicePrincipal("apigateway.amazonaws.com"),
                    action="lambda:InvokeFunction",
                    source_arn=f"arn:aws:execute-api:{self.target_region}:{self.account_id}:{api.rest_api_id}/*/POST/chat"
                )
            elif api_name == 'createUser':
                process_user_data_fn.add_permission(
                    "AllowCreateUserAPIPutInvoke",
                    principal=iam.ServicePrincipal("apigateway.amazonaws.com"),
                    action="lambda:InvokeFunction",
                    source_arn=f"arn:aws:execute-api:{self.target_region}:{self.account_id}:{api.rest_api_id}/*/PUT/addUser"
                )
            elif api_name in ['QueryAnalyticsAPI1', 'QueryAnalyticsAPI2']:
                query_analytics_api_fn.add_permission(
                    f"Allow{api_name}Invoke",
                    principal=iam.ServicePrincipal("apigateway.amazonaws.com"),
                    action="lambda:InvokeFunction",
                    source_arn=f"arn:aws:execute-api:{self.target_region}:{self.account_id}:{api.rest_api_id}/*/POST/*"
                )
            elif api_name == 'ReferralsApi':
                referrals_api_handler_fn.add_permission(
                    "AllowReferralsAPIInvoke",
                    principal=iam.ServicePrincipal("apigateway.amazonaws.com"),
                    action="lambda:InvokeFunction",
                    source_arn=f"arn:aws:execute-api:{self.target_region}:{self.account_id}:{api.rest_api_id}/*/*"
                )

        # WebSocket API permissions
        for api_name, (api, stage) in api_config.websocket_apis.items():
            if api_name == 'ReferralChatbotWebSocket':
                referral_chatbot_fn.add_permission(
                    "AllowReferralChatbotWebSocketInvoke",
                    principal=iam.ServicePrincipal("apigateway.amazonaws.com"),
                    action="lambda:InvokeFunction",
                    source_arn=f"arn:aws:execute-api:{self.target_region}:{self.account_id}:{api.api_id}/*/*"
                )
            elif api_name == 'UserFeedbackWebSocketAPI':
                process_user_data_fn.add_permission(
                    "AllowUserFeedbackWebSocketInvoke",
                    principal=iam.ServicePrincipal("apigateway.amazonaws.com"),
                    action="lambda:InvokeFunction",
                    source_arn=f"arn:aws:execute-api:{self.target_region}:{self.account_id}:{api.api_id}/*/*"
                )
            elif api_name == 'AnalyticsWebSocketAPI':
                query_analytics_api_fn.add_permission(
                    "AllowAnalyticsWebSocketInvoke",
                    principal=iam.ServicePrincipal("apigateway.amazonaws.com"),
                    action="lambda:InvokeFunction",
                    source_arn=f"arn:aws:execute-api:{self.target_region}:{self.account_id}:{api.api_id}/*/*"
                )
            elif api_name == 'ReferralsWebSocketAPI':
                referrals_api_handler_fn.add_permission(
                    "AllowReferralsWebSocketInvoke",
                    principal=iam.ServicePrincipal("apigateway.amazonaws.com"),
                    action="lambda:InvokeFunction",
                    source_arn=f"arn:aws:execute-api:{self.target_region}:{self.account_id}:{api.api_id}/*/*"
                )

        # Output the DynamoDB table names
        # --- Comprehensive Outputs ---

        # 1. Amplify Outputs
        CfnOutput(
            self, "AmplifyAppId",
            value=amplify_app.app_id,
            description=f"Amplify App ID for {self.env_name}",
            export_name=f"{self.stack_name}-AmplifyAppId"
        )

        CfnOutput(
            self, "AmplifyAppUrl",
            value=f"https://frontend-code.{amplify_app.app_id}.amplifyapp.com",
            description=f"URL of the Amplify App for {self.env_name}",
            export_name=f"{self.stack_name}-AmplifyAppUrl"
        )

        CfnOutput(
            self, "AmplifyConsoleUrl",
            value=f"https://{self.target_region}.console.aws.amazon.com/amplify/apps/{amplify_app.app_id}",
            description=f"Amplify Console URL for {self.env_name}",
            export_name=f"{self.stack_name}-AmplifyConsoleUrl"
        )

        # 2. Cognito Outputs
        CfnOutput(
            self, "CognitoUserPoolId",
            value=user_pool.user_pool_id,
            description=f"Cognito User Pool ID for {self.env_name}",
            export_name=f"{self.stack_name}-UserPoolId"
        )

        CfnOutput(
            self, "CognitoUserPoolClientId",
            value=user_pool_client.user_pool_client_id,
            description=f"Cognito User Pool Client ID for {self.env_name}",
            export_name=f"{self.stack_name}-UserPoolClientId"
        )

        CfnOutput(
            self, "CognitoIdentityPoolId",
            value=identity_pool.ref,
            description=f"Cognito Identity Pool ID for {self.env_name}",
            export_name=f"{self.stack_name}-IdentityPoolId"
        )

        CfnOutput(
            self, "CognitoUserPoolDomain",
            value=f"https://brightpoint-{self.env_name}.auth.{self.target_region}.amazoncognito.com",
            description=f"Cognito User Pool Domain for {self.env_name}",
            export_name=f"{self.stack_name}-UserPoolDomain"
        )

        # 3. REST API Endpoints
        for api_name, api in api_config.rest_apis.items():
            CfnOutput(
                self, f"{api_name}Url",
                value=f"https://{api.rest_api_id}.execute-api.{self.target_region}.amazonaws.com/{api.deployment_stage.stage_name}/",
                description=f"URL of the {api_name} REST API for {self.env_name}",
                export_name=f"{self.stack_name}-{api_name}Url"
            )

            CfnOutput(
                self, f"{api_name}Id",
                value=api.rest_api_id,
                description=f"API Gateway ID for {api_name} in {self.env_name}",
                export_name=f"{self.stack_name}-{api_name}Id"
            )

        # 5. Environment Configuration Summary
        config_summary = {
            "environment": self.env_name,
            "target_region": self.target_region,
            "amplifyAppId": amplify_app.app_id,
            "userPoolId": user_pool.user_pool_id,
            "userPoolClientId": user_pool_client.user_pool_client_id,
            "identityPoolId": identity_pool.ref,
        }

        CfnOutput(
            self, "FrontendConfigSummary",
            value=json.dumps(config_summary, indent=2),
            description=f"Frontend configuration summary for {self.env_name}",
            export_name=f"{self.stack_name}-ConfigSummary"
        )

        # 6. DynamoDB Table Names (already in your code, but grouped here)
        CfnOutput(
            self, "WebSocketConnectionsTableName",
            value=websocket_connections_table.table_name,
            description="WebSocket Connections Table Name",
            export_name=f"{self.stack_name}-WebSocketTableName"
        )

        CfnOutput(
            self, "PerplexityQueryCacheTableName",
            value=perplexity_query_cache_table.table_name,
            description="Perplexity Query Cache Table Name",
            export_name=f"{self.stack_name}-CacheTableName"
        )

        CfnOutput(
            self, "QueryAnalyticsTableName",
            value=query_analytics_table.table_name,
            description="Query Analytics Table Name",
            export_name=f"{self.stack_name}-AnalyticsTableName"
        )

        CfnOutput(
            self, "ReferralDataTableName",
            value=referral_data_table.table_name,
            description="Referral Data Table Name",
            export_name=f"{self.stack_name}-ReferralTableName"
        )

        CfnOutput(
            self, "UserDataTableName",
            value=user_data_table.table_name,
            description="User Data Table Name",
            export_name=f"{self.stack_name}-UserTableName"
        )

    # Keep all the existing role policy methods unchanged
    def add_referral_chatbot_role_policies(self, role, account_id):
        """Add all necessary policies to the referralChatbotLambda role"""
        role.add_managed_policy(
            iam.ManagedPolicy.from_aws_managed_policy_name("service-role/AWSLambdaBasicExecutionRole")
        )

        role.add_to_policy(
            iam.PolicyStatement(
                actions=[
                    "translate:*",
                    "comprehend:DetectDominantLanguage",
                    "cloudwatch:GetMetricStatistics",
                    "cloudwatch:ListMetrics",
                    "s3:ListAllMyBuckets",
                    "s3:ListBucket",
                    "s3:GetBucketLocation",
                    "iam:ListRoles",
                    "iam:GetRole"
                ],
                resources=["*"]
            )
        )

        role.add_to_policy(
            iam.PolicyStatement(
                actions=[
                    "dynamodb:GetItem",
                    "dynamodb:PutItem",
                    "dynamodb:UpdateItem",
                    "dynamodb:DeleteItem",
                    "dynamodb:Query",
                    "dynamodb:Scan"
                ],
                resources=[
                    f"arn:aws:dynamodb:us-east-1:{account_id}:table/referral_data*",
                    f"arn:aws:dynamodb:us-east-1:{account_id}:table/user_data*"
                ]
            )
        )

        role.add_to_policy(
            iam.PolicyStatement(
                actions=["bedrock:InvokeModel"],
                resources=["*"]
            )
        )

        role.add_to_policy(
            iam.PolicyStatement(
                actions=["lambda:InvokeFunction"],
                resources=[f"arn:aws:lambda:us-east-1:{account_id}:function:perplexityLambda*"]
            )
        )

        role.add_to_policy(
            iam.PolicyStatement(
                actions=["execute-api:ManageConnections"],
                resources=["arn:aws:execute-api:*:*:*/*/POST/@connections/*"]
            )
        )

        role.add_to_policy(
            iam.PolicyStatement(
                effect=iam.Effect.ALLOW,
                actions=["logs:CreateLogGroup"],
                resources=[f"arn:aws:logs:us-east-1:{account_id}:*"]
            )
        )

        role.add_to_policy(
            iam.PolicyStatement(
                effect=iam.Effect.ALLOW,
                actions=[
                    "logs:CreateLogStream",
                    "logs:PutLogEvents"
                ],
                resources=[
                    f"arn:aws:logs:us-east-1:{account_id}:log-group:/aws/lambda/referralChatbotLambda*:*"
                ]
            )
        )

    # Add all other role policy methods here (I'll skip them for brevity as they follow the same pattern)
    # Just update the resource ARNs to include wildcards where appropriate
    # For example: table/referral_data* instead of table/referral_data
    # And: function:perplexityLambda* instead of function:perplexityLambda

    def add_perplexity_lambda_role_policies(self, role, account_id):
        """Add all necessary policies to the perplexityLambda role"""
        role.add_managed_policy(
            iam.ManagedPolicy.from_aws_managed_policy_name("service-role/AWSLambdaBasicExecutionRole")
        )

        role.add_to_policy(
            iam.PolicyStatement(
                actions=[
                    "translate:*",
                    "comprehend:DetectDominantLanguage",
                    "cloudwatch:GetMetricStatistics",
                    "cloudwatch:ListMetrics",
                    "s3:ListAllMyBuckets",
                    "s3:ListBucket",
                    "s3:GetBucketLocation",
                    "iam:ListRoles",
                    "iam:GetRole"
                ],
                resources=["*"]
            )
        )

        role.add_to_policy(
            iam.PolicyStatement(
                actions=["dynamodb:*", "dax:*"],
                resources=["*"]
            )
        )

        role.add_to_policy(
            iam.PolicyStatement(
                effect=iam.Effect.ALLOW,
                actions=["logs:CreateLogGroup"],
                resources=[f"arn:aws:logs:us-east-1:{account_id}:*"]
            )
        )

        role.add_to_policy(
            iam.PolicyStatement(
                effect=iam.Effect.ALLOW,
                actions=[
                    "logs:CreateLogStream",
                    "logs:PutLogEvents"
                ],
                resources=[
                    f"arn:aws:logs:us-east-1:{account_id}:log-group:/aws/lambda/perplexityLambda*:*"
                ]
            )
        )

    def add_process_user_data_role_policies(self, role, account_id):
        """Add all necessary policies to the ProcessUserData role"""
        role.add_managed_policy(
            iam.ManagedPolicy.from_aws_managed_policy_name("service-role/AWSLambdaBasicExecutionRole")
        )

        role.add_to_policy(
            iam.PolicyStatement(
                actions=[
                    "translate:*",
                    "comprehend:DetectDominantLanguage",
                    "cloudwatch:GetMetricStatistics",
                    "cloudwatch:ListMetrics",
                    "s3:ListAllMyBuckets",
                    "s3:ListBucket",
                    "s3:GetBucketLocation",
                    "iam:ListRoles",
                    "iam:GetRole"
                ],
                resources=["*"]
            )
        )

        role.add_to_policy(
            iam.PolicyStatement(
                actions=["dynamodb:*", "dax:*"],
                resources=["*"]
            )
        )

        role.add_to_policy(
            iam.PolicyStatement(
                actions=["execute-api:ManageConnections"],
                resources=["arn:aws:execute-api:*:*:*/*/POST/@connections/*"]
            )
        )

        role.add_to_policy(
            iam.PolicyStatement(
                effect=iam.Effect.ALLOW,
                actions=["logs:CreateLogGroup"],
                resources=[f"arn:aws:logs:us-east-1:{account_id}:*"]
            )
        )

        role.add_to_policy(
            iam.PolicyStatement(
                effect=iam.Effect.ALLOW,
                actions=[
                    "logs:CreateLogStream",
                    "logs:PutLogEvents"
                ],
                resources=[
                    f"arn:aws:logs:us-east-1:{account_id}:log-group:/aws/lambda/ProcessUserData*:*"
                ]
            )
        )

    def add_query_analytics_backfill_role_policies(self, role, account_id):
        """Add all necessary policies to the query-analytics-backfill role"""
        role.add_to_policy(
            iam.PolicyStatement(
                effect=iam.Effect.ALLOW,
                actions=[
                    "dynamodb:DescribeStream",
                    "dynamodb:GetRecords",
                    "dynamodb:GetShardIterator",
                    "dynamodb:ListStreams",
                    "logs:CreateLogGroup",
                    "logs:CreateLogStream",
                    "logs:PutLogEvents"
                ],
                resources=["*"]
            )
        )

        role.add_to_policy(
            iam.PolicyStatement(
                actions=["dynamodb:*", "dax:*"],
                resources=["*"]
            )
        )

        role.add_to_policy(
            iam.PolicyStatement(
                actions=[
                    "application-autoscaling:DeleteScalingPolicy",
                    "application-autoscaling:DeregisterScalableTarget",
                    "application-autoscaling:DescribeScalableTargets",
                    "application-autoscaling:DescribeScalingActivities",
                    "application-autoscaling:DescribeScalingPolicies",
                    "application-autoscaling:PutScalingPolicy",
                    "application-autoscaling:RegisterScalableTarget",
                    "cloudwatch:DeleteAlarms",
                    "cloudwatch:DescribeAlarmHistory",
                    "cloudwatch:DescribeAlarms",
                    "cloudwatch:DescribeAlarmsForMetric",
                    "cloudwatch:GetMetricStatistics",
                    "cloudwatch:ListMetrics",
                    "cloudwatch:PutMetricAlarm",
                    "cloudwatch:GetMetricData",
                    "datapipeline:ActivatePipeline",
                    "datapipeline:CreatePipeline",
                    "datapipeline:DeletePipeline",
                    "datapipeline:DescribeObjects",
                    "datapipeline:DescribePipelines",
                    "datapipeline:GetPipelineDefinition",
                    "datapipeline:ListPipelines",
                    "datapipeline:PutPipelineDefinition",
                    "datapipeline:QueryObjects",
                    "ec2:DescribeVpcs",
                    "ec2:DescribeSubnets",
                    "ec2:DescribeSecurityGroups",
                    "iam:GetRole",
                    "iam:ListRoles",
                    "kms:DescribeKey",
                    "kms:ListAliases",
                    "sns:CreateTopic",
                    "sns:DeleteTopic",
                    "sns:ListSubscriptions",
                    "sns:ListSubscriptionsByTopic",
                    "sns:ListTopics",
                    "sns:Subscribe",
                    "sns:Unsubscribe",
                    "sns:SetTopicAttributes",
                    "lambda:CreateFunction",
                    "lambda:ListFunctions",
                    "lambda:ListEventSourceMappings",
                    "lambda:CreateEventSourceMapping",
                    "lambda:DeleteEventSourceMapping",
                    "lambda:GetFunctionConfiguration",
                    "lambda:DeleteFunction",
                    "resource-groups:ListGroups",
                    "resource-groups:ListGroupResources",
                    "resource-groups:GetGroup",
                    "resource-groups:GetGroupQuery",
                    "resource-groups:DeleteGroup",
                    "resource-groups:CreateGroup",
                    "tag:GetResources",
                    "kinesis:ListStreams",
                    "kinesis:DescribeStream",
                    "kinesis:DescribeStreamSummary"
                ],
                resources=["*"]
            )
        )

        role.add_to_policy(
            iam.PolicyStatement(
                actions=["cloudwatch:GetInsightRuleReport"],
                resources=["arn:aws:cloudwatch:*:*:insight-rule/DynamoDBContributorInsights*"]
            )
        )

        role.add_to_policy(
            iam.PolicyStatement(
                actions=["iam:PassRole"],
                resources=["*"],
                conditions={
                    "StringLike": {
                        "iam:PassedToService": [
                            "application-autoscaling.amazonaws.com",
                            "application-autoscaling.amazonaws.com.cn",
                            "dax.amazonaws.com"
                        ]
                    }
                }
            )
        )

        role.add_to_policy(
            iam.PolicyStatement(
                effect=iam.Effect.ALLOW,
                actions=["iam:CreateServiceLinkedRole"],
                resources=["*"],
                conditions={
                    "StringEquals": {
                        "iam:AWSServiceName": [
                            "replication.dynamodb.amazonaws.com",
                            "dax.amazonaws.com",
                            "dynamodb.application-autoscaling.amazonaws.com",
                            "contributorinsights.dynamodb.amazonaws.com",
                            "kinesisreplication.dynamodb.amazonaws.com"
                        ]
                    }
                }
            )
        )

        role.add_to_policy(
            iam.PolicyStatement(
                effect=iam.Effect.ALLOW,
                actions=["logs:CreateLogGroup"],
                resources=[f"arn:aws:logs:us-east-1:{account_id}:*"]
            )
        )

        role.add_to_policy(
            iam.PolicyStatement(
                effect=iam.Effect.ALLOW,
                actions=[
                    "logs:CreateLogStream",
                    "logs:PutLogEvents"
                ],
                resources=[
                    f"arn:aws:logs:us-east-1:{account_id}:log-group:/aws/lambda/query-analytics-backfill*:*"
                ]
            )
        )

    def add_query_analytics_api_role_policies(self, role, account_id):
        role.add_to_policy(
            iam.PolicyStatement(
                effect=iam.Effect.ALLOW,
                actions=[
                    "dynamodb:DescribeStream",
                    "dynamodb:GetRecords",
                    "dynamodb:GetShardIterator",
                    "dynamodb:ListStreams",
                    "logs:CreateLogGroup",
                    "logs:CreateLogStream",
                    "logs:PutLogEvents"
                ],
                resources=["*"]
            )
        )

        role.add_to_policy(
            iam.PolicyStatement(
                actions=["dynamodb:*", "dax:*"],
                resources=["*"]
            )
        )

        role.add_to_policy(
            iam.PolicyStatement(
                actions=[
                    "application-autoscaling:DeleteScalingPolicy",
                    "application-autoscaling:DeregisterScalableTarget",
                    "application-autoscaling:DescribeScalableTargets",
                    "application-autoscaling:DescribeScalingActivities",
                    "application-autoscaling:DescribeScalingPolicies",
                    "application-autoscaling:PutScalingPolicy",
                    "application-autoscaling:RegisterScalableTarget",
                    "cloudwatch:DeleteAlarms",
                    "cloudwatch:DescribeAlarmHistory",
                    "cloudwatch:DescribeAlarms",
                    "cloudwatch:DescribeAlarmsForMetric",
                    "cloudwatch:GetMetricStatistics",
                    "cloudwatch:ListMetrics",
                    "cloudwatch:PutMetricAlarm",
                    "cloudwatch:GetMetricData",
                    "datapipeline:ActivatePipeline",
                    "datapipeline:CreatePipeline",
                    "datapipeline:DeletePipeline",
                    "datapipeline:DescribeObjects",
                    "datapipeline:DescribePipelines",
                    "datapipeline:GetPipelineDefinition",
                    "datapipeline:ListPipelines",
                    "datapipeline:PutPipelineDefinition",
                    "datapipeline:QueryObjects",
                    "ec2:DescribeVpcs",
                    "ec2:DescribeSubnets",
                    "ec2:DescribeSecurityGroups",
                    "iam:GetRole",
                    "iam:ListRoles",
                    "kms:DescribeKey",
                    "kms:ListAliases",
                    "sns:CreateTopic",
                    "sns:DeleteTopic",
                    "sns:ListSubscriptions",
                    "sns:ListSubscriptionsByTopic",
                    "sns:ListTopics",
                    "sns:Subscribe",
                    "sns:Unsubscribe",
                    "sns:SetTopicAttributes",
                    "lambda:CreateFunction",
                    "lambda:ListFunctions",
                    "lambda:ListEventSourceMappings",
                    "lambda:CreateEventSourceMapping",
                    "lambda:DeleteEventSourceMapping",
                    "lambda:GetFunctionConfiguration",
                    "lambda:DeleteFunction",
                    "resource-groups:ListGroups",
                    "resource-groups:ListGroupResources",
                    "resource-groups:GetGroup",
                    "resource-groups:GetGroupQuery",
                    "resource-groups:DeleteGroup",
                    "resource-groups:CreateGroup",
                    "tag:GetResources",
                    "kinesis:ListStreams",
                    "kinesis:DescribeStream",
                    "kinesis:DescribeStreamSummary"
                ],
                resources=["*"]
            )
        )

        role.add_to_policy(
            iam.PolicyStatement(
                actions=["cloudwatch:GetInsightRuleReport"],
                resources=["arn:aws:cloudwatch:*:*:insight-rule/DynamoDBContributorInsights*"]
            )
        )

        role.add_to_policy(
            iam.PolicyStatement(
                actions=["iam:PassRole"],
                resources=["*"],
                conditions={
                    "StringLike": {
                        "iam:PassedToService": [
                            "application-autoscaling.amazonaws.com",
                            "application-autoscaling.amazonaws.com.cn",
                            "dax.amazonaws.com"
                        ]
                    }
                }
            )
        )

        role.add_to_policy(
            iam.PolicyStatement(
                effect=iam.Effect.ALLOW,
                actions=["iam:CreateServiceLinkedRole"],
                resources=["*"],
                conditions={
                    "StringEquals": {
                        "iam:AWSServiceName": [
                            "replication.dynamodb.amazonaws.com",
                            "dax.amazonaws.com",
                            "dynamodb.application-autoscaling.amazonaws.com",
                            "contributorinsights.dynamodb.amazonaws.com",
                            "kinesisreplication.dynamodb.amazonaws.com"
                        ]
                    }
                }
            )
        )

        role.add_to_policy(
            iam.PolicyStatement(
                effect=iam.Effect.ALLOW,
                actions=["logs:CreateLogGroup"],
                resources=[f"arn:aws:logs:us-east-1:{account_id}:*"]
            )
        )

        role.add_to_policy(
            iam.PolicyStatement(
                effect=iam.Effect.ALLOW,
                actions=[
                    "logs:CreateLogStream",
                    "logs:PutLogEvents"
                ],
                resources=[
                    f"arn:aws:logs:us-east-1:{account_id}:log-group:/aws/lambda/query-analytics-api*:*"
                ]
            )
        )

    def add_referrals_api_handler_role_policies(self, role, account_id):
        role.add_to_policy(
            iam.PolicyStatement(
                sid="CloudWatchLogsFullAccess",
                effect=iam.Effect.ALLOW,
                actions=[
                    "logs:*",
                    "cloudwatch:GenerateQuery"
                ],
                resources=["*"]
            )
        )

        role.add_to_policy(
            iam.PolicyStatement(
                effect=iam.Effect.ALLOW,
                actions=[
                    "logs:CreateLogGroup",
                    "logs:CreateLogStream",
                    "logs:PutLogEvents"
                ],
                resources=["*"]
            )
        )

        role.add_to_policy(
            iam.PolicyStatement(
                actions=["dynamodb:*", "dax:*"],
                resources=["*"]
            )
        )

        role.add_to_policy(
            iam.PolicyStatement(
                actions=[
                    "application-autoscaling:DeleteScalingPolicy",
                    "application-autoscaling:DeregisterScalableTarget",
                    "application-autoscaling:DescribeScalableTargets",
                    "application-autoscaling:DescribeScalingActivities",
                    "application-autoscaling:DescribeScalingPolicies",
                    "application-autoscaling:PutScalingPolicy",
                    "application-autoscaling:RegisterScalableTarget",
                    "cloudwatch:DeleteAlarms",
                    "cloudwatch:DescribeAlarmHistory",
                    "cloudwatch:DescribeAlarms",
                    "cloudwatch:DescribeAlarmsForMetric",
                    "cloudwatch:GetMetricStatistics",
                    "cloudwatch:ListMetrics",
                    "cloudwatch:PutMetricAlarm",
                    "cloudwatch:GetMetricData",
                    "datapipeline:ActivatePipeline",
                    "datapipeline:CreatePipeline",
                    "datapipeline:DeletePipeline",
                    "datapipeline:DescribeObjects",
                    "datapipeline:DescribePipelines",
                    "datapipeline:GetPipelineDefinition",
                    "datapipeline:ListPipelines",
                    "datapipeline:PutPipelineDefinition",
                    "datapipeline:QueryObjects",
                    "ec2:DescribeVpcs",
                    "ec2:DescribeSubnets",
                    "ec2:DescribeSecurityGroups",
                    "iam:GetRole",
                    "iam:ListRoles",
                    "kms:DescribeKey",
                    "kms:ListAliases",
                    "sns:CreateTopic",
                    "sns:DeleteTopic",
                    "sns:ListSubscriptions",
                    "sns:ListSubscriptionsByTopic",
                    "sns:ListTopics",
                    "sns:Subscribe",
                    "sns:Unsubscribe",
                    "sns:SetTopicAttributes",
                    "lambda:CreateFunction",
                    "lambda:ListFunctions",
                    "lambda:ListEventSourceMappings",
                    "lambda:CreateEventSourceMapping",
                    "lambda:DeleteEventSourceMapping",
                    "lambda:GetFunctionConfiguration",
                    "lambda:DeleteFunction",
                    "resource-groups:ListGroups",
                    "resource-groups:ListGroupResources",
                    "resource-groups:GetGroup",
                    "resource-groups:GetGroupQuery",
                    "resource-groups:DeleteGroup",
                    "resource-groups:CreateGroup",
                    "tag:GetResources",
                    "kinesis:ListStreams",
                    "kinesis:DescribeStream",
                    "kinesis:DescribeStreamSummary"
                ],
                resources=["*"]
            )
        )

        role.add_to_policy(
            iam.PolicyStatement(
                actions=["cloudwatch:GetInsightRuleReport"],
                resources=["arn:aws:cloudwatch:*:*:insight-rule/DynamoDBContributorInsights*"]
            )
        )

        role.add_to_policy(
            iam.PolicyStatement(
                actions=["iam:PassRole"],
                resources=["*"],
                conditions={
                    "StringLike": {
                        "iam:PassedToService": [
                            "application-autoscaling.amazonaws.com",
                            "application-autoscaling.amazonaws.com.cn",
                            "dax.amazonaws.com"
                        ]
                    }
                }
            )
        )

        role.add_to_policy(
            iam.PolicyStatement(
                effect=iam.Effect.ALLOW,
                actions=["iam:CreateServiceLinkedRole"],
                resources=["*"],
                conditions={
                    "StringEquals": {
                        "iam:AWSServiceName": [
                            "replication.dynamodb.amazonaws.com",
                            "dax.amazonaws.com",
                            "dynamodb.application-autoscaling.amazonaws.com",
                            "contributorinsights.dynamodb.amazonaws.com",
                            "kinesisreplication.dynamodb.amazonaws.com"
                        ]
                    }
                }
            )
        )

        role.add_to_policy(
            iam.PolicyStatement(
                effect=iam.Effect.ALLOW,
                actions=[
                    "logs:CreateLogGroup",
                    "logs:CreateLogStream",
                    "logs:PutLogEvents"
                ],
                resources=["arn:aws:logs:*:*:*"]
            )
        )

        role.add_to_policy(
            iam.PolicyStatement(
                effect=iam.Effect.ALLOW,
                actions=[
                    "dynamodb:PutItem",
                    "dynamodb:GetItem",
                    "dynamodb:UpdateItem",
                    "dynamodb:DeleteItem",
                    "dynamodb:Scan",
                    "dynamodb:Query"
                ],
                resources=["arn:aws:dynamodb:*:*:table/Referrals*", "arn:aws:dynamodb:*:*:table/referral_data*"]
            )
        )

        role.add_to_policy(
            iam.PolicyStatement(
                effect=iam.Effect.ALLOW,
                actions=["execute-api:ManageConnections"],
                resources=["arn:aws:execute-api:*:*:*/*/POST/@connections/*"]
            )
        )

        role.add_to_policy(
            iam.PolicyStatement(
                effect=iam.Effect.ALLOW,
                actions=[
                    "dynamodb:PutItem",
                    "dynamodb:GetItem",
                    "dynamodb:DeleteItem",
                    "dynamodb:Scan"
                ],
                resources=["arn:aws:dynamodb:*:*:table/WebSocketConnections*"]
            )
        )

        role.add_to_policy(
            iam.PolicyStatement(
                effect=iam.Effect.ALLOW,
                actions=[
                    "dynamodb:GetItem",
                    "dynamodb:Query",
                    "dynamodb:Scan"
                ],
                resources=[f"arn:aws:dynamodb:us-east-1:{account_id}:table/referral_data*"]
            )
        )

    def add_sms_chat_integration_role_policies(self, role, account_id):
        """Add all necessary policies to the smsChatIntegration role"""
        role.add_to_policy(
            iam.PolicyStatement(
                effect=iam.Effect.ALLOW,
                actions=["apigateway:*"],
                resources=["arn:aws:apigateway:*::/*"]
            )
        )

        role.add_to_policy(
            iam.PolicyStatement(
                sid="SNSFullAccess",
                effect=iam.Effect.ALLOW,
                actions=["sns:*"],
                resources=["*"]
            )
        )

        role.add_to_policy(
            iam.PolicyStatement(
                sid="SMSAccessViaSNS",
                effect=iam.Effect.ALLOW,
                actions=[
                    "sms-voice:DescribeVerifiedDestinationNumbers",
                    "sms-voice:CreateVerifiedDestinationNumber",
                    "sms-voice:SendDestinationNumberVerificationCode",
                    "sms-voice:SendTextMessage",
                    "sms-voice:DeleteVerifiedDestinationNumber",
                    "sms-voice:VerifyDestinationNumber",
                    "sms-voice:DescribeAccountAttributes",
                    "sms-voice:DescribeSpendLimits",
                    "sms-voice:DescribePhoneNumbers",
                    "sms-voice:SetTextMessageSpendLimitOverride",
                    "sms-voice:DescribeOptedOutNumbers",
                    "sms-voice:DeleteOptedOutNumber"
                ],
                resources=["*"],
                conditions={
                    "StringEquals": {
                        "aws:CalledViaLast": "sns.amazonaws.com"
                    }
                }
            )
        )

        role.add_to_policy(
            iam.PolicyStatement(
                effect=iam.Effect.ALLOW,
                actions=[
                    "execute-api:Invoke",
                    "execute-api:ManageConnections"
                ],
                resources=["arn:aws:execute-api:*:*:*"]
            )
        )

        role.add_to_policy(
            iam.PolicyStatement(
                actions=[
                    "dynamodb:*",
                    "dax:*",
                    "application-autoscaling:DeleteScalingPolicy",
                    "application-autoscaling:DeregisterScalableTarget",
                    "application-autoscaling:DescribeScalableTargets",
                    "application-autoscaling:DescribeScalingActivities",
                    "application-autoscaling:DescribeScalingPolicies",
                    "application-autoscaling:PutScalingPolicy",
                    "application-autoscaling:RegisterScalableTarget",
                    "cloudwatch:DeleteAlarms",
                    "cloudwatch:DescribeAlarmHistory",
                    "cloudwatch:DescribeAlarms",
                    "cloudwatch:DescribeAlarmsForMetric",
                    "cloudwatch:GetMetricStatistics",
                    "cloudwatch:ListMetrics",
                    "cloudwatch:PutMetricAlarm",
                    "cloudwatch:GetMetricData",
                    "datapipeline:ActivatePipeline",
                    "datapipeline:CreatePipeline",
                    "datapipeline:DeletePipeline",
                    "datapipeline:DescribeObjects",
                    "datapipeline:DescribePipelines",
                    "datapipeline:GetPipelineDefinition",
                    "datapipeline:ListPipelines",
                    "datapipeline:PutPipelineDefinition",
                    "datapipeline:QueryObjects",
                    "ec2:DescribeVpcs",
                    "ec2:DescribeSubnets",
                    "ec2:DescribeSecurityGroups",
                    "iam:GetRole",
                    "iam:ListRoles",
                    "kms:DescribeKey",
                    "kms:ListAliases",
                    "sns:CreateTopic",
                    "sns:DeleteTopic",
                    "sns:ListSubscriptions",
                    "sns:ListSubscriptionsByTopic",
                    "sns:ListTopics",
                    "sns:Subscribe",
                    "sns:Unsubscribe",
                    "sns:SetTopicAttributes",
                    "lambda:CreateFunction",
                    "lambda:ListFunctions",
                    "lambda:ListEventSourceMappings",
                    "lambda:CreateEventSourceMapping",
                    "lambda:DeleteEventSourceMapping",
                    "lambda:GetFunctionConfiguration",
                    "lambda:DeleteFunction",
                    "resource-groups:ListGroups",
                    "resource-groups:ListGroupResources",
                    "resource-groups:GetGroup",
                    "resource-groups:GetGroupQuery",
                    "resource-groups:DeleteGroup",
                    "resource-groups:CreateGroup",
                    "tag:GetResources",
                    "kinesis:ListStreams",
                    "kinesis:DescribeStream",
                    "kinesis:DescribeStreamSummary"
                ],
                resources=["*"]
            )
        )

        role.add_to_policy(
            iam.PolicyStatement(
                actions=["cloudwatch:GetInsightRuleReport"],
                resources=["arn:aws:cloudwatch:*:*:insight-rule/DynamoDBContributorInsights*"]
            )
        )

        role.add_to_policy(
            iam.PolicyStatement(
                actions=["iam:PassRole"],
                resources=["*"],
                conditions={
                    "StringLike": {
                        "iam:PassedToService": [
                            "application-autoscaling.amazonaws.com",
                            "application-autoscaling.amazonaws.com.cn",
                            "dax.amazonaws.com"
                        ]
                    }
                }
            )
        )

        role.add_to_policy(
            iam.PolicyStatement(
                effect=iam.Effect.ALLOW,
                actions=["iam:CreateServiceLinkedRole"],
                resources=["*"],
                conditions={
                    "StringEquals": {
                        "iam:AWSServiceName": [
                            "replication.dynamodb.amazonaws.com",
                            "dax.amazonaws.com",
                            "dynamodb.application-autoscaling.amazonaws.com",
                            "contributorinsights.dynamodb.amazonaws.com",
                            "kinesisreplication.dynamodb.amazonaws.com"
                        ]
                    }
                }
            )
        )

        role.add_to_policy(
            iam.PolicyStatement(
                effect=iam.Effect.ALLOW,
                actions=["logs:CreateLogGroup"],
                resources=[f"arn:aws:logs:us-east-1:{account_id}:*"]
            )
        )

        role.add_to_policy(
            iam.PolicyStatement(
                effect=iam.Effect.ALLOW,
                actions=[
                    "logs:CreateLogStream",
                    "logs:PutLogEvents"
                ],
                resources=[
                    f"arn:aws:logs:us-east-1:{account_id}:log-group:/aws/lambda/smsChatIntegration*:*"
                ]
            )
        )

        role.add_to_policy(
            iam.PolicyStatement(
                effect=iam.Effect.ALLOW,
                actions=["sts:AssumeRole"],
                resources=["arn:aws:iam::514811724234:role/crossAccountPinpointAccess"]
            )
        )

    def add_query_analytics_stream_processor_role_policies(self, role, account_id):
        role.add_to_policy(
            iam.PolicyStatement(
                effect=iam.Effect.ALLOW,
                actions=[
                    "dynamodb:DescribeStream",
                    "dynamodb:GetRecords",
                    "dynamodb:GetShardIterator",
                    "dynamodb:ListStreams",
                    "logs:CreateLogGroup",
                    "logs:CreateLogStream",
                    "logs:PutLogEvents"
                ],
                resources=["*"]
            )
        )

        role.add_to_policy(
            iam.PolicyStatement(
                actions=[
                    "dynamodb:*",
                    "dax:*",
                    "application-autoscaling:DeleteScalingPolicy",
                    "application-autoscaling:DeregisterScalableTarget",
                    "application-autoscaling:DescribeScalableTargets",
                    "application-autoscaling:DescribeScalingActivities",
                    "application-autoscaling:DescribeScalingPolicies",
                    "application-autoscaling:PutScalingPolicy",
                    "application-autoscaling:RegisterScalableTarget",
                    "cloudwatch:DeleteAlarms",
                    "cloudwatch:DescribeAlarmHistory",
                    "cloudwatch:DescribeAlarms",
                    "cloudwatch:DescribeAlarmsForMetric",
                    "cloudwatch:GetMetricStatistics",
                    "cloudwatch:ListMetrics",
                    "cloudwatch:PutMetricAlarm",
                    "cloudwatch:GetMetricData",
                    "datapipeline:ActivatePipeline",
                    "datapipeline:CreatePipeline",
                    "datapipeline:DeletePipeline",
                    "datapipeline:DescribeObjects",
                    "datapipeline:DescribePipelines",
                    "datapipeline:GetPipelineDefinition",
                    "datapipeline:ListPipelines",
                    "datapipeline:PutPipelineDefinition",
                    "datapipeline:QueryObjects",
                    "ec2:DescribeVpcs",
                    "ec2:DescribeSubnets",
                    "ec2:DescribeSecurityGroups",
                    "iam:GetRole",
                    "iam:ListRoles",
                    "kms:DescribeKey",
                    "kms:ListAliases",
                    "sns:CreateTopic",
                    "sns:DeleteTopic",
                    "sns:ListSubscriptions",
                    "sns:ListSubscriptionsByTopic",
                    "sns:ListTopics",
                    "sns:Subscribe",
                    "sns:Unsubscribe",
                    "sns:SetTopicAttributes",
                    "lambda:CreateFunction",
                    "lambda:ListFunctions",
                    "lambda:ListEventSourceMappings",
                    "lambda:CreateEventSourceMapping",
                    "lambda:DeleteEventSourceMapping",
                    "lambda:GetFunctionConfiguration",
                    "lambda:DeleteFunction",
                    "resource-groups:ListGroups",
                    "resource-groups:ListGroupResources",
                    "resource-groups:GetGroup",
                    "resource-groups:GetGroupQuery",
                    "resource-groups:DeleteGroup",
                    "resource-groups:CreateGroup",
                    "tag:GetResources",
                    "kinesis:ListStreams",
                    "kinesis:DescribeStream",
                    "kinesis:DescribeStreamSummary"
                ],
                resources=["*"]
            )
        )

        role.add_to_policy(
            iam.PolicyStatement(
                actions=["cloudwatch:GetInsightRuleReport"],
                resources=["arn:aws:cloudwatch:*:*:insight-rule/DynamoDBContributorInsights*"]
            )
        )

        role.add_to_policy(
            iam.PolicyStatement(
                actions=["iam:PassRole"],
                resources=["*"],
                conditions={
                    "StringLike": {
                        "iam:PassedToService": [
                            "application-autoscaling.amazonaws.com",
                            "application-autoscaling.amazonaws.com.cn",
                            "dax.amazonaws.com"
                        ]
                    }
                }
            )
        )

        role.add_to_policy(
            iam.PolicyStatement(
                effect=iam.Effect.ALLOW,
                actions=["iam:CreateServiceLinkedRole"],
                resources=["*"],
                conditions={
                    "StringEquals": {
                        "iam:AWSServiceName": [
                            "replication.dynamodb.amazonaws.com",
                            "dax.amazonaws.com",
                            "dynamodb.application-autoscaling.amazonaws.com",
                            "contributorinsights.dynamodb.amazonaws.com",
                            "kinesisreplication.dynamodb.amazonaws.com"
                        ]
                    }
                }
            )
        )

        role.add_to_policy(
            iam.PolicyStatement(
                effect=iam.Effect.ALLOW,
                actions=["logs:CreateLogGroup"],
                resources=[f"arn:aws:logs:us-east-1:{account_id}:*"]
            )
        )

        role.add_to_policy(
            iam.PolicyStatement(
                effect=iam.Effect.ALLOW,
                actions=[
                    "logs:CreateLogStream",
                    "logs:PutLogEvents"
                ],
                resources=[
                    f"arn:aws:logs:us-east-1:{account_id}:log-group:/aws/lambda/query-analytics-stream-processor*:*"
                ]
            )
        )