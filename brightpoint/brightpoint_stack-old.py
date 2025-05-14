# from aws_cdk import (
#     Stack,
#     aws_lambda as lambda_,
#     aws_dynamodb as dynamodb,
#     aws_apigateway as apigateway,
#     aws_iam as iam,
#     CfnOutput,
#     RemovalPolicy,
#     Duration,
#     aws_amplify_alpha as amplify,
#     aws_cognito as cognito,
#     aws_s3_assets as s3_assets,
# )
# from constructs import Construct
# import os

# class BrightpointStack(Stack):

#     def __init__(self, scope: Construct, construct_id: str, **kwargs) -> None:
#         super().__init__(scope, construct_id, **kwargs)

#         account_id = "108782065617"

#         # Import existing DynamoDB tables
#         referral_data_table = dynamodb.Table.from_table_name(
#             self, "ReferralDataTable", "referral_data"
#         )

#         user_data_table = dynamodb.Table.from_table_name(
#             self, "UserDataTable", "user_data"
#         )

#         websocket_connections_table = dynamodb.Table.from_table_name(
#             self, "WebSocketConnectionsTable", "WebSocketConnections"
#         )

#         perplexity_query_cache_table = dynamodb.Table.from_table_name(
#             self, "perplexity_query_cacheTable", "perplexity_query_cache"
#         )

#         query_analytics_table = dynamodb.Table.from_table_name(
#             self, "query_analyticsTable", "query_analytics"
#         )

#         # DynamoDB Tables CDK Configuration for New Environment

#         # Table: WebSocketConnections
#         # websocket_connections_table = dynamodb.Table(
#         #     self, 'WebSocketConnectionsTable',
#         #     table_name='WebSocketConnections',
#         #     partition_key=dynamodb.Attribute(name='connectionId', type=dynamodb.AttributeType.STRING),
#         #     billing_mode=dynamodb.BillingMode.PAY_PER_REQUEST,
#         #     removal_policy=RemovalPolicy.RETAIN,  # Change as needed
#         # )

#         # Table: perplexity_query_cache
#         # perplexity_query_cache_table = dynamodb.Table(
#         #     self, 'perplexity_query_cacheTable',
#         #     table_name='perplexity_query_cache',
#         #     partition_key=dynamodb.Attribute(name='query_id', type=dynamodb.AttributeType.STRING),
#         #     billing_mode=dynamodb.BillingMode.PAY_PER_REQUEST,
#         #     removal_policy=RemovalPolicy.RETAIN,  # Change as needed
#         # )

#         # Table: query_analytics
#         # query_analytics_table = dynamodb.Table(
#         #     self, 'query_analyticsTable',
#         #     table_name='query_analytics',
#         #     partition_key=dynamodb.Attribute(name='query_text', type=dynamodb.AttributeType.STRING),
#         #     sort_key=dynamodb.Attribute(name='Zipcode', type=dynamodb.AttributeType.STRING),
#         #     billing_mode=dynamodb.BillingMode.PAY_PER_REQUEST,
#         #     removal_policy=RemovalPolicy.RETAIN,  # Change as needed
#         # )

#         # Table: referral_data
#         # referral_data_table = dynamodb.Table(
#         #     self, 'referral_dataTable',
#         #     table_name='referral_data',
#         #     partition_key=dynamodb.Attribute(name='referral_id', type=dynamodb.AttributeType.STRING),
#         #     billing_mode=dynamodb.BillingMode.PAY_PER_REQUEST,
#         #     removal_policy=RemovalPolicy.RETAIN,  # Change as needed
#         # )

#         # Table: user_data
#         # user_data_table = dynamodb.Table(
#         #     self, 'user_dataTable',
#         #     table_name='user_data',
#         #     partition_key=dynamodb.Attribute(name='user_id', type=dynamodb.AttributeType.STRING),
#         #     billing_mode=dynamodb.BillingMode.PAY_PER_REQUEST,
#         #     stream=dynamodb.StreamViewType.NEW_AND_OLD_IMAGES,
#         #     removal_policy=RemovalPolicy.RETAIN,  # Change as needed
#         # )

#         # Global Secondary Indexes for user_data
#         # user_data_table.add_global_secondary_index(
#         #     index_name='Phone-index',
#         #     partition_key=dynamodb.Attribute(name='Phone', type=dynamodb.AttributeType.STRING),
#         #     projection_type=dynamodb.ProjectionType.ALL,
#         # )


#         # Import existing API Gateways - REST APIs
#         rest_api_ids = {
#             "ReferralChatbotAPI": "pncxzrq0r9",
#             "ProcessUserRestAPI": "kahgke45yd",  # Also known as createUser
#             "UserDashboardAPI": "329yd7xxm0",
#             "QueryAnalyticsAPI1": "adt0bzrd3e",
#             "QueryAnalyticsAPI2": "ite99ljw0b",
#             "ReferralsApi": "twi9ghqfhl"
#         }

#         rest_apis = {}

#         # Import REST APIs
#         for api_name, api_id in rest_api_ids.items():
#             rest_apis[api_name] = apigateway.RestApi.from_rest_api_id(
#                 self, f"{api_name}Id",
#                 rest_api_id=api_id
#             )

#         # Import existing API Gateways - WebSocket APIs
#         websocket_api_ids = {
#             "ReferralChatbotWebSocket": "lajngh4a22",
#             "ProcessUserWebSocketAPI": "p8ea1v23i0",  # Also known as UserFeedbackWebSocketAPI
#             "AnalyticsWebSocketAPI": "duqhouj11e",
#             "ReferralsWebSocketAPI": "z0ebrmmyd0"
#         }

#         # Import existing Lambda functions
#         referral_chatbot_fn = lambda_.Function.from_function_name(
#             self, "ReferralChatbotLambdaFn", "referralChatbotLambda"
#         )

#         perplexity_lambda_fn = lambda_.Function.from_function_name(
#             self, "PerplexityLambdaFn", "perplexityLambda"
#         )

#         process_user_data_fn = lambda_.Function.from_function_name(
#             self, "ProcessUserDataFn", "ProcessUserData"
#         )

#         query_analytics_backfill_fn = lambda_.Function.from_function_name(
#             self, "QueryAnalyticsBackfillFn", "query-analytics-backfill"
#         )

#         query_analytics_api_fn = lambda_.Function.from_function_name(
#             self, "QueryAnalyticsApiFn", "query-analytics-api"
#         )

#         referrals_api_handler_fn = lambda_.Function.from_function_name(
#             self, "ReferralsApiHandlerFn", "ReferralsApiHandler"
#         )

#         sms_chat_integration_fn = lambda_.Function.from_function_name(
#             self, "SmsChatIntegrationFn", "smsChatIntegration"
#         )

#         query_analytics_stream_processor_fn = lambda_.Function.from_function_name(
#             self, "QueryAnalyticsStreamProcessorFn", "query-analytics-stream-processor"
#         )

#                 # --- Cognito User Pool ---
#         user_pool = cognito.UserPool(
#             self, "BrightpointUserPool",
#             self_sign_up_enabled=True,
#             sign_in_aliases=cognito.SignInAliases(email=True),
#             auto_verify=cognito.AutoVerifiedAttrs(email=True),
#             account_recovery=cognito.AccountRecovery.EMAIL_ONLY
#         )

#         user_pool_client = cognito.UserPoolClient(
#             self, "BrightpointUserPoolClient",
#             user_pool=user_pool,
#             generate_secret=False,
#             auth_flows=cognito.AuthFlow(user_password=True)
#         )

#         identity_pool = cognito.CfnIdentityPool(
#             self, "BrightpointIdentityPool",
#             allow_unauthenticated_identities=False,
#             cognito_identity_providers=[{
#                 "clientId": user_pool_client.user_pool_client_id,
#                 "providerName": user_pool.user_pool_provider_name,
#             }]
#         )

#         # --- Cognito Outputs ---
#         CfnOutput(self, "CognitoUserPoolId", value=user_pool.user_pool_id)
#         CfnOutput(self, "CognitoUserPoolClientId", value=user_pool_client.user_pool_client_id)
#         CfnOutput(self, "CognitoIdentityPoolId", value=identity_pool.ref)

#         # --- Amplify Hosting ---
#        # Create an Amplify App for manual deployment
#         amplify_app = amplify.App(
#             self, "BrightpointManualAmplifyApp",
#             app_name="brightpoint-manual-app",
#             description="Amplify App for manually deployed frontend",
#             auto_branch_deletion=True
#         )

#         # Add a default branch (you can name it 'prod' or 'main')
#         main_branch = amplify_app.add_branch("prod")

#         # Output the Amplify URL
#         CfnOutput(
#         self, "AmplifyManualAppConsoleUrl",
#         value=f"https://{amplify_app.app_id}.amplifyapp.com",
#         description="URL of the Amplify App (manually deploy frontend to prod branch)"
# )




#         # Option to create new Lambda functions (commented out as we're using existing ones)
#         """
#         # Create Lambda execution roles
#         referral_chatbot_role = iam.Role(
#             self, "ReferralChatbotRole",
#             role_name="referralChatbotLambda-role",
#             assumed_by=iam.ServicePrincipal("lambda.amazonaws.com"),
#             description="Role for Brightpoint Referral Chatbot Lambda function"
#         )
        
#         # Add policies for referralChatbotLambda role
#         self.add_referral_chatbot_role_policies(referral_chatbot_role, account_id)
        
#         # Create perplexityLambda role
#         perplexity_lambda_role = iam.Role(
#             self, "PerplexityLambdaRole",
#             role_name="perplexityLambda-role",
#             assumed_by=iam.ServicePrincipal("lambda.amazonaws.com"),
#             description="Role for Perplexity Lambda function"
#         )
        
#         # Add policies for perplexityLambda role
#         self.add_perplexity_lambda_role_policies(perplexity_lambda_role, account_id)
        
#         # Create ProcessUserData Lambda role
#         process_user_data_role = iam.Role(
#             self, "ProcessUserDataRole",
#             role_name="LambdaUserDynamoDBRole",
#             assumed_by=iam.ServicePrincipal("lambda.amazonaws.com"),
#             description="Role for Process User Data Lambda function"
#         )
        
#         # Add policies for ProcessUserData role
#         self.add_process_user_data_role_policies(process_user_data_role, account_id)
        
#         # Create query-analytics-backfill Lambda role
#         query_analytics_backfill_role = iam.Role(
#             self, "QueryAnalyticsBackfillRole",
#             role_name="query-analytics-backfill-role-1osb4uwf",
#             assumed_by=iam.ServicePrincipal("lambda.amazonaws.com"),
#             description="Role for Query Analytics Backfill Lambda function"
#         )
        
#         # Add policies for query-analytics-backfill role
#         self.add_query_analytics_backfill_role_policies(query_analytics_backfill_role, account_id)
        
#         # Create query-analytics-api Lambda role
#         query_analytics_api_role = iam.Role(
#             self, "QueryAnalyticsApiRole",
#             role_name="query-analytics-api-role",
#             assumed_by=iam.ServicePrincipal("lambda.amazonaws.com"),
#             description="Role for Query Analytics API Lambda function"
#         )
        
#         # Add policies for query-analytics-api role
#         self.add_query_analytics_api_role_policies(query_analytics_api_role, account_id)
        
#         # Create ReferralsApiHandler Lambda role
#         referrals_api_handler_role = iam.Role(
#             self, "ReferralsApiHandlerRole",
#             role_name="ReferralsApiHandler-role",
#             assumed_by=iam.ServicePrincipal("lambda.amazonaws.com"),
#             description="Role for Referrals API Handler Lambda function"
#         )
        
#         # Add policies for ReferralsApiHandler role
#         self.add_referrals_api_handler_role_policies(referrals_api_handler_role, account_id)
        
#         # Create smsChatIntegration Lambda role
#         sms_chat_integration_role = iam.Role(
#             self, "SmsChatIntegrationRole",
#             role_name="smsChatIntegration-role-ihkg71ku",
#             assumed_by=iam.ServicePrincipal("lambda.amazonaws.com"),
#             description="Role for SMS Chat Integration Lambda function"
#         )
        
#         # Add policies for smsChatIntegration role
#         self.add_sms_chat_integration_role_policies(sms_chat_integration_role, account_id)
        
#         # Create query-analytics-stream-processor Lambda role
#         query_analytics_stream_processor_role = iam.Role(
#             self, "QueryAnalyticsStreamProcessorRole",
#             role_name="query-analytics-stream-processor-role-ipnlblc1",
#             assumed_by=iam.ServicePrincipal("lambda.amazonaws.com"),
#             description="Role for Query Analytics Stream Processor Lambda function"
#         )
        
#         # Add policies for query-analytics-stream-processor role
#         self.add_query_analytics_stream_processor_role_policies(query_analytics_stream_processor_role, account_id)

                
#         # Create the referralChatbotLambda function
#         # This function includes bedrockAgent.py and getServiceCategories.py as helper modules
#         referral_chatbot_fn = lambda_.Function(
#             self, "ReferralChatbotLambdaFn",
#             function_name="referralChatbotLambda",
#             runtime=lambda_.Runtime.PYTHON_3_12,
#             code=lambda_.Code.from_asset("brightpoint/referral_chatbot"),
#             handler="referralChatbotLambda.lambda_handler",
#             role=referral_chatbot_role,
#             timeout=Duration.seconds(900),  # 15 minutes
#             memory_size=1024,
#             architecture=lambda_.Architecture.X86_64
#         )
        
#         # Create the perplexityLambda function
#         perplexity_lambda_fn = lambda_.Function(
#             self, "PerplexityLambdaFn",
#             function_name="perplexityLambda",
#             runtime=lambda_.Runtime.PYTHON_3_12,
#             code=lambda_.Code.from_asset("brightpoint/perplexity_lambda"),
#             handler="lambda_function.lambda_handler",
#             role=perplexity_lambda_role,
#             timeout=Duration.seconds(900),  # 15 minutes
#             memory_size=2048,
#             architecture=lambda_.Architecture.X86_64,
#             environment={
#                 "PERPLEXITY_API_KEY": "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"
#             }
#         )
        
#         # Create the ProcessUserData function
#         process_user_data_fn = lambda_.Function(
#             self, "ProcessUserDataFn",
#             function_name="ProcessUserData",
#             runtime=lambda_.Runtime.PYTHON_3_12,
#             code=lambda_.Code.from_asset("brightpoint/process_user_data"),
#             handler="lambda_function.lambda_handler",
#             role=process_user_data_role,
#             timeout=Duration.seconds(900),  # 15 minutes
#             memory_size=1024,
#             architecture=lambda_.Architecture.X86_64
#         )
        
#         # Create the query-analytics-api function
#         query_analytics_api_fn = lambda_.Function(
#             self, "QueryAnalyticsApiFn",
#             function_name="query-analytics-api",
#             runtime=lambda_.Runtime.PYTHON_3_12,
#             code=lambda_.Code.from_asset("brightpoint/query_analytics_api"),
#             handler="lambda_function.lambda_handler",
#             role=query_analytics_api_role,
#             timeout=Duration.seconds(300),  # 5 minutes
#             memory_size=1024,
#             architecture=lambda_.Architecture.X86_64
#         )
        
#         # Create the ReferralsApiHandler function
#         referrals_api_handler_fn = lambda_.Function(
#             self, "ReferralsApiHandlerFn",
#             function_name="ReferralsApiHandler",
#             runtime=lambda_.Runtime.PYTHON_3_12,
#             code=lambda_.Code.from_asset("brightpoint/referrals_api_handler"),
#             handler="lambda_function.lambda_handler",
#             role=referrals_api_handler_role,
#             timeout=Duration.seconds(300),  # 5 minutes
#             memory_size=1024,
#             architecture=lambda_.Architecture.X86_64
#         )
        
#         # Create the query-analytics-backfill function
#         query_analytics_backfill_fn = lambda_.Function(
#             self, "QueryAnalyticsBackfillFn",
#             function_name="query-analytics-backfill",
#             runtime=lambda_.Runtime.PYTHON_3_12,
#             code=lambda_.Code.from_asset("brightpoint/query_analytics_backfill"),
#             handler="lambda_function.lambda_handler",
#             role=query_analytics_backfill_role,
#             timeout=Duration.seconds(900),  # 15 minutes
#             memory_size=512,
#             architecture=lambda_.Architecture.X86_64
#         )
        
#         # Create the smsChatIntegration function
#         sms_chat_integration_fn = lambda_.Function(
#             self, "SmsChatIntegrationFn",
#             function_name="smsChatIntegration",
#             runtime=lambda_.Runtime.PYTHON_3_12,
#             code=lambda_.Code.from_asset("brightpoint/sms_chat_integration"),
#             handler="lambda_function.lambda_handler",
#             role=sms_chat_integration_role,
#             timeout=Duration.seconds(300),  # 5 minutes
#             memory_size=2048,
#             architecture=lambda_.Architecture.X86_64,
#             environment={
#                 "USER_TABLE_NAME": "user_data",
#                 "LOGIN_URL": "https://www.google.com/",
#                 "PINPOINT_APPLICATION_ID": "38a47a3f1a734353a4621a2cf90ada0c",
#                 "API_GATEWAY_URL": "https://pncxzrq0r9.execute-api.us-east-1.amazonaws.com/dev/chat",
#                 "HTTP_TIMEOUT": "60",
#                 "REGISTRATION_URL": "https://www.google.com/"
#             }
#         )
        
#         # Add SNS trigger permission (cross-account)
#         sms_chat_integration_fn.add_permission(
#             "AllowSNSInvoke",
#             principal=iam.ServicePrincipal("sns.amazonaws.com"),
#             action="lambda:InvokeFunction",
#             source_arn="arn:aws:sns:us-east-1:514811724234:PinpointV3Stack-responselambdatwoWaySMStopicC0D976B7-ntcREJoZGzuH"
#         )
        
#         # Create the query-analytics-stream-processor function
#         query_analytics_stream_processor_fn = lambda_.Function(
#             self, "QueryAnalyticsStreamProcessorFn",
#             function_name="query-analytics-stream-processor",
#             runtime=lambda_.Runtime.PYTHON_3_12,
#             code=lambda_.Code.from_asset("brightpoint/query_analytics_stream_processor"),
#             handler="lambda_function.lambda_handler",
#             role=query_analytics_stream_processor_role,
#             timeout=Duration.seconds(300),  # 5 minutes
#             memory_size=512,  # Rounded up from 511
#             architecture=lambda_.Architecture.X86_64
#         )
        
#         # Add DynamoDB stream event source mapping
#         query_analytics_stream_processor_fn.add_event_source_mapping(
#             "UserDataStreamMapping",
#             event_source_arn=user_data_table.stream_arn,  # Assuming user_data_table is already defined
#             starting_position=lambda_.StartingPosition.LATEST,
#             batch_size=100,
#             max_batching_window_in_seconds=0,
#             parallelization_factor=1,
#             maximum_record_age_in_seconds=-1,
#             bisect_batch_on_function_error=False,
#             maximum_retry_attempts=-1,
#             tumbling_window_in_seconds=0
#         )
        
#         ### API GW Triggers for Lambda
#         referral_chatbot_fn.add_permission(
#             "AllowRestApiPost",
#             principal=iam.ServicePrincipal("apigateway.amazonaws.com"),
#             action="lambda:InvokeFunction",
#             source_arn=f"arn:aws:execute-api:{self.region}:{account_id}:pncxzrq0r9/*/POST/chat"
#         )
        
#         # Add WebSocket API trigger permissions
#         referral_chatbot_fn.add_permission(
#             "AllowWebSocketConnect",
#             principal=iam.ServicePrincipal("apigateway.amazonaws.com"),
#             action="lambda:InvokeFunction",
#             source_arn=f"arn:aws:execute-api:{self.region}:{account_id}:lajngh4a22/*/$connect"
#         )
        
#         referral_chatbot_fn.add_permission(
#             "AllowWebSocketDisconnect",
#             principal=iam.ServicePrincipal("apigateway.amazonaws.com"),
#             action="lambda:InvokeFunction",
#             source_arn=f"arn:aws:execute-api:{self.region}:{account_id}:lajngh4a22/*/$disconnect"
#         )
        
#         referral_chatbot_fn.add_permission(
#             "AllowWebSocketQuery",
#             principal=iam.ServicePrincipal("apigateway.amazonaws.com"),
#             action="lambda:InvokeFunction",
#             source_arn=f"arn:aws:execute-api:{self.region}:{account_id}:lajngh4a22/*/query"
#         )
        
#         # Add REST API trigger permissions
#         query_analytics_api_fn.add_permission(
#             "AllowQueryAnalyticsApi1",
#             principal=iam.ServicePrincipal("apigateway.amazonaws.com"),
#             action="lambda:InvokeFunction",
#             source_arn=f"arn:aws:execute-api:{self.region}:{account_id}:adt0bzrd3e/*/POST/analytics/all"
#         )
        
#         query_analytics_api_fn.add_permission(
#             "AllowQueryAnalyticsApi2",
#             principal=iam.ServicePrincipal("apigateway.amazonaws.com"),
#             action="lambda:InvokeFunction",
#             source_arn=f"arn:aws:execute-api:{self.region}:{account_id}:ite99ljw0b/*/POST/analytics/queries"
#         )
        
#         # Add WebSocket API trigger permissions
#         query_analytics_api_fn.add_permission(
#             "AllowAnalyticsWebSocketConnect",
#             principal=iam.ServicePrincipal("apigateway.amazonaws.com"),
#             action="lambda:InvokeFunction",
#             source_arn=f"arn:aws:execute-api:{self.region}:{account_id}:duqhouj11e/*/$connect"
#         )
        
#         query_analytics_api_fn.add_permission(
#             "AllowAnalyticsWebSocketDisconnect",
#             principal=iam.ServicePrincipal("apigateway.amazonaws.com"),
#             action="lambda:InvokeFunction",
#             source_arn=f"arn:aws:execute-api:{self.region}:{account_id}:duqhouj11e/*/$disconnect"
#         )
        
#         query_analytics_api_fn.add_permission(
#             "AllowAnalyticsWebSocketDefault",
#             principal=iam.ServicePrincipal("apigateway.amazonaws.com"),
#             action="lambda:InvokeFunction",
#             source_arn=f"arn:aws:execute-api:{self.region}:{account_id}:duqhouj11e/*/$default"
#         )
        
#         query_analytics_api_fn.add_permission(
#             "AllowAnalyticsWebSocketGetAnalytics",
#             principal=iam.ServicePrincipal("apigateway.amazonaws.com"),
#             action="lambda:InvokeFunction",
#             source_arn=f"arn:aws:execute-api:{self.region}:{account_id}:duqhouj11e/*/getAnalytics"
#         )
        
#         # Add REST API trigger permissions
#         referrals_api_methods = [
#             ("GET", "/referrals"),
#             ("POST", "/referrals"),
#             ("PUT", "/referrals"),
#             ("DELETE", "/referrals"),
#             ("GET", "/referrals/*"),
#             ("POST", "/referrals/*"),
#             ("PUT", "/referrals/*"),
#             ("DELETE", "/referrals/*"),
#             ("POST", "/referrals/search")
#         ]
        
#         for method, path in referrals_api_methods:
#             permission_id = f"AllowReferralsApi{method}{path.replace('/', '').replace('*', 'Id')}"
#             referrals_api_handler_fn.add_permission(
#                 permission_id,
#                 principal=iam.ServicePrincipal("apigateway.amazonaws.com"),
#                 action="lambda:InvokeFunction",
#                 source_arn=f"arn:aws:execute-api:{self.region}:{account_id}:twi9ghqfhl/*/{method}{path}"
#             )
        
#         # Add WebSocket API trigger permissions
#         referrals_websocket_routes = [
#             "$connect",
#             "$disconnect",
#             "$default",
#             "getReferral",
#             "createReferral",
#             "updateReferral",
#             "getReferrals",
#             "deleteReferral",
#             "searchReferrals"
#         ]
        
#         for route in referrals_websocket_routes:
#             permission_id = f"AllowReferralsWebSocket{route.replace('$', '')}"
#             referrals_api_handler_fn.add_permission(
#                 permission_id,
#                 principal=iam.ServicePrincipal("apigateway.amazonaws.com"),
#                 action="lambda:InvokeFunction",
#                 source_arn=f"arn:aws:execute-api:{self.region}:{account_id}:z0ebrmmyd0/*/{route}"
#             )
            
#         # Add REST API trigger permission
#         process_user_data_fn.add_permission(
#             "AllowCreateUserApi",
#             principal=iam.ServicePrincipal("apigateway.amazonaws.com"),
#             action="lambda:InvokeFunction",
#             source_arn=f"arn:aws:execute-api:{self.region}:{account_id}:kahgke45yd/*/POST/addUser"
#         )
        
#         # Add WebSocket API trigger permissions
#         user_feedback_routes = [
#             "$connect",
#             "$disconnect",
#             "getUser",
#             "updateUser",
#             "sendFeedback"
#         ]
        
#         for route in user_feedback_routes:
#             permission_id = f"AllowUserFeedbackWebSocket{route.replace('$', '')}"
#             process_user_data_fn.add_permission(
#                 permission_id,
#                 principal=iam.ServicePrincipal("apigateway.amazonaws.com"),
#                 action="lambda:InvokeFunction",
#                 source_arn=f"arn:aws:execute-api:{self.region}:{account_id}:p8ea1v23i0/*/{route}"
#             )

#         """

#         # Output the REST API URLs
#         for api_name, api_id in rest_api_ids.items():
#             output_stage = "dev" if api_name not in ["ReferralChatbotAPI", "ProcessUserRestAPI"] else "prod"
#             CfnOutput(
#                 self, f"{api_name}Url",
#                 value=f"https://{api_id}.execute-api.{self.region}.amazonaws.com/{output_stage}/",
#                 description=f"URL of the {api_name} REST API"
#             )

#         # Output the WebSocket API URLs
#         for api_name, api_id in websocket_api_ids.items():
#             output_stage = "dev" if api_name not in ["ReferralChatbotWebSocket", "ProcessUserWebSocketAPI"] else "prod"
#             CfnOutput(
#                 self, f"{api_name}Url",
#                 value=f"wss://{api_id}.execute-api.{self.region}.amazonaws.com/{output_stage}/",
#                 description=f"URL of the {api_name} WebSocket API"
#             )

#         # Output the DynamoDB table names
#         CfnOutput(
#             self, "WebSocketConnectionsTableName",
#             value=websocket_connections_table.table_name,
#             description="WebSocket Connections Table Name"
#         )

#         CfnOutput(
#             self, "PerplexityQueryCacheTableName",
#             value=perplexity_query_cache_table.table_name,
#             description="Perplexity Query Cache Table Name"
#         )

#         CfnOutput(
#             self, "QueryAnalyticsTableName",
#             value=query_analytics_table.table_name,
#             description="Query Analytics Table Name"
#         )

#         CfnOutput(
#             self, "ReferralDataTableName",
#             value=referral_data_table.table_name,
#             description="Referral Data Table Name (Imported)"
#         )

#         CfnOutput(
#             self, "UserDataTableName",
#             value=user_data_table.table_name,
#             description="User Data Table Name (Imported)"
#         )

        

#     def add_referral_chatbot_role_policies(self, role, account_id):
#         """Add all necessary policies to the referralChatbotLambda role"""

#         # Add Lambda basic execution
#         role.add_managed_policy(
#             iam.ManagedPolicy.from_aws_managed_policy_name("service-role/AWSLambdaBasicExecutionRole")
#         )

#         # Add permissions for Translate and Comprehend
#         role.add_to_policy(
#             iam.PolicyStatement(
#                 actions=[
#                     "translate:*",
#                     "comprehend:DetectDominantLanguage",
#                     "cloudwatch:GetMetricStatistics",
#                     "cloudwatch:ListMetrics",
#                     "s3:ListAllMyBuckets",
#                     "s3:ListBucket",
#                     "s3:GetBucketLocation",
#                     "iam:ListRoles",
#                     "iam:GetRole"
#                 ],
#                 resources=["*"]
#             )
#         )

#         # Add DynamoDB permissions
#         role.add_to_policy(
#             iam.PolicyStatement(
#                 actions=[
#                     "dynamodb:GetItem",
#                     "dynamodb:PutItem",
#                     "dynamodb:UpdateItem",
#                     "dynamodb:DeleteItem",
#                     "dynamodb:Query",
#                     "dynamodb:Scan"
#                 ],
#                 resources=[
#                     f"arn:aws:dynamodb:us-east-1:{account_id}:table/referral_data",
#                     f"arn:aws:dynamodb:us-east-1:{account_id}:table/user_data"
#                 ]
#             )
#         )

#         # Add Bedrock permissions
#         role.add_to_policy(
#             iam.PolicyStatement(
#                 actions=["bedrock:InvokeModel"],
#                 resources=["*"]
#             )
#         )

#         # Add Lambda invoke permissions
#         role.add_to_policy(
#             iam.PolicyStatement(
#                 actions=["lambda:InvokeFunction"],
#                 resources=[f"arn:aws:lambda:us-east-1:{account_id}:function:perplexityLambda"]
#             )
#         )

#         # Add WebSocket permissions
#         role.add_to_policy(
#             iam.PolicyStatement(
#                 actions=["execute-api:ManageConnections"],
#                 resources=["arn:aws:execute-api:*:*:*/*/POST/@connections/*"]
#             )
#         )

#         # Add CloudWatch Logs permissions
#         role.add_to_policy(
#             iam.PolicyStatement(
#                 effect=iam.Effect.ALLOW,
#                 actions=["logs:CreateLogGroup"],
#                 resources=[f"arn:aws:logs:us-east-1:{account_id}:*"]
#             )
#         )

#         role.add_to_policy(
#             iam.PolicyStatement(
#                 effect=iam.Effect.ALLOW,
#                 actions=[
#                     "logs:CreateLogStream",
#                     "logs:PutLogEvents"
#                 ],
#                 resources=[
#                     f"arn:aws:logs:us-east-1:{account_id}:log-group:/aws/lambda/referralChatbotLambda:*"
#                 ]
#             )
#         )

#     def add_perplexity_lambda_role_policies(self, role, account_id):
#         """Add all necessary policies to the perplexityLambda role"""

#         # Add Lambda basic execution
#         role.add_managed_policy(
#             iam.ManagedPolicy.from_aws_managed_policy_name("service-role/AWSLambdaBasicExecutionRole")
#         )

#         # Add permissions for Translate and Comprehend
#         role.add_to_policy(
#             iam.PolicyStatement(
#                 actions=[
#                     "translate:*",
#                     "comprehend:DetectDominantLanguage",
#                     "cloudwatch:GetMetricStatistics",
#                     "cloudwatch:ListMetrics",
#                     "s3:ListAllMyBuckets",
#                     "s3:ListBucket",
#                     "s3:GetBucketLocation",
#                     "iam:ListRoles",
#                     "iam:GetRole"
#                 ],
#                 resources=["*"]
#             )
#         )

#         # Add DynamoDB permissions (full access from policy)
#         role.add_to_policy(
#             iam.PolicyStatement(
#                 actions=["dynamodb:*", "dax:*"],
#                 resources=["*"]
#             )
#         )

#         # Add CloudWatch Logs permissions
#         role.add_to_policy(
#             iam.PolicyStatement(
#                 effect=iam.Effect.ALLOW,
#                 actions=["logs:CreateLogGroup"],
#                 resources=[f"arn:aws:logs:us-east-1:{account_id}:*"]
#             )
#         )

#         role.add_to_policy(
#             iam.PolicyStatement(
#                 effect=iam.Effect.ALLOW,
#                 actions=[
#                     "logs:CreateLogStream",
#                     "logs:PutLogEvents"
#                 ],
#                 resources=[
#                     f"arn:aws:logs:us-east-1:{account_id}:log-group:/aws/lambda/perplexityLambda:*"
#                 ]
#             )
#         )

#     def add_process_user_data_role_policies(self, role, account_id):
#         """Add all necessary policies to the ProcessUserData role"""

#         # Add Lambda basic execution
#         role.add_managed_policy(
#             iam.ManagedPolicy.from_aws_managed_policy_name("service-role/AWSLambdaBasicExecutionRole")
#         )

#         # Add permissions for Translate and Comprehend
#         role.add_to_policy(
#             iam.PolicyStatement(
#                 actions=[
#                     "translate:*",
#                     "comprehend:DetectDominantLanguage",
#                     "cloudwatch:GetMetricStatistics",
#                     "cloudwatch:ListMetrics",
#                     "s3:ListAllMyBuckets",
#                     "s3:ListBucket",
#                     "s3:GetBucketLocation",
#                     "iam:ListRoles",
#                     "iam:GetRole"
#                 ],
#                 resources=["*"]
#             )
#         )

#         # Add DynamoDB permissions (full access from policy)
#         role.add_to_policy(
#             iam.PolicyStatement(
#                 actions=["dynamodb:*", "dax:*"],
#                 resources=["*"]
#             )
#         )

#         # Add WebSocket permissions
#         role.add_to_policy(
#             iam.PolicyStatement(
#                 actions=["execute-api:ManageConnections"],
#                 resources=["arn:aws:execute-api:*:*:*/*/POST/@connections/*"]
#             )
#         )

#         # Add CloudWatch Logs permissions
#         role.add_to_policy(
#             iam.PolicyStatement(
#                 effect=iam.Effect.ALLOW,
#                 actions=["logs:CreateLogGroup"],
#                 resources=[f"arn:aws:logs:us-east-1:{account_id}:*"]
#             )
#         )

#         role.add_to_policy(
#             iam.PolicyStatement(
#                 effect=iam.Effect.ALLOW,
#                 actions=[
#                     "logs:CreateLogStream",
#                     "logs:PutLogEvents"
#                 ],
#                 resources=[
#                     f"arn:aws:logs:us-east-1:{account_id}:log-group:/aws/lambda/ProcessUserData:*"
#                 ]
#             )
#         )

#     def add_query_analytics_backfill_role_policies(self, role, account_id):
#         """Add all necessary policies to the query-analytics-backfill role"""

#         # Add Lambda basic execution with DynamoDB stream permissions
#         role.add_to_policy(
#             iam.PolicyStatement(
#                 effect=iam.Effect.ALLOW,
#                 actions=[
#                     "dynamodb:DescribeStream",
#                     "dynamodb:GetRecords",
#                     "dynamodb:GetShardIterator",
#                     "dynamodb:ListStreams",
#                     "logs:CreateLogGroup",
#                     "logs:CreateLogStream",
#                     "logs:PutLogEvents"
#                 ],
#                 resources=["*"]
#             )
#         )

#         # Add DynamoDB full access
#         role.add_to_policy(
#             iam.PolicyStatement(
#                 actions=["dynamodb:*", "dax:*"],
#                 resources=["*"]
#             )
#         )

#         # Add various AWS service permissions for DynamoDB operations
#         role.add_to_policy(
#             iam.PolicyStatement(
#                 actions=[
#                     "application-autoscaling:DeleteScalingPolicy",
#                     "application-autoscaling:DeregisterScalableTarget",
#                     "application-autoscaling:DescribeScalableTargets",
#                     "application-autoscaling:DescribeScalingActivities",
#                     "application-autoscaling:DescribeScalingPolicies",
#                     "application-autoscaling:PutScalingPolicy",
#                     "application-autoscaling:RegisterScalableTarget",
#                     "cloudwatch:DeleteAlarms",
#                     "cloudwatch:DescribeAlarmHistory",
#                     "cloudwatch:DescribeAlarms",
#                     "cloudwatch:DescribeAlarmsForMetric",
#                     "cloudwatch:GetMetricStatistics",
#                     "cloudwatch:ListMetrics",
#                     "cloudwatch:PutMetricAlarm",
#                     "cloudwatch:GetMetricData",
#                     "datapipeline:ActivatePipeline",
#                     "datapipeline:CreatePipeline",
#                     "datapipeline:DeletePipeline",
#                     "datapipeline:DescribeObjects",
#                     "datapipeline:DescribePipelines",
#                     "datapipeline:GetPipelineDefinition",
#                     "datapipeline:ListPipelines",
#                     "datapipeline:PutPipelineDefinition",
#                     "datapipeline:QueryObjects",
#                     "ec2:DescribeVpcs",
#                     "ec2:DescribeSubnets",
#                     "ec2:DescribeSecurityGroups",
#                     "iam:GetRole",
#                     "iam:ListRoles",
#                     "kms:DescribeKey",
#                     "kms:ListAliases",
#                     "sns:CreateTopic",
#                     "sns:DeleteTopic",
#                     "sns:ListSubscriptions",
#                     "sns:ListSubscriptionsByTopic",
#                     "sns:ListTopics",
#                     "sns:Subscribe",
#                     "sns:Unsubscribe",
#                     "sns:SetTopicAttributes",
#                     "lambda:CreateFunction",
#                     "lambda:ListFunctions",
#                     "lambda:ListEventSourceMappings",
#                     "lambda:CreateEventSourceMapping",
#                     "lambda:DeleteEventSourceMapping",
#                     "lambda:GetFunctionConfiguration",
#                     "lambda:DeleteFunction",
#                     "resource-groups:ListGroups",
#                     "resource-groups:ListGroupResources",
#                     "resource-groups:GetGroup",
#                     "resource-groups:GetGroupQuery",
#                     "resource-groups:DeleteGroup",
#                     "resource-groups:CreateGroup",
#                     "tag:GetResources",
#                     "kinesis:ListStreams",
#                     "kinesis:DescribeStream",
#                     "kinesis:DescribeStreamSummary"
#                 ],
#                 resources=["*"]
#             )
#         )

#         # Add CloudWatch Insights access
#         role.add_to_policy(
#             iam.PolicyStatement(
#                 actions=["cloudwatch:GetInsightRuleReport"],
#                 resources=["arn:aws:cloudwatch:*:*:insight-rule/DynamoDBContributorInsights*"]
#             )
#         )

#         # Add IAM PassRole permissions
#         role.add_to_policy(
#             iam.PolicyStatement(
#                 actions=["iam:PassRole"],
#                 resources=["*"],
#                 conditions={
#                     "StringLike": {
#                         "iam:PassedToService": [
#                             "application-autoscaling.amazonaws.com",
#                             "application-autoscaling.amazonaws.com.cn",
#                             "dax.amazonaws.com"
#                         ]
#                     }
#                 }
#             )
#         )

#         # Add IAM CreateServiceLinkedRole permissions
#         role.add_to_policy(
#             iam.PolicyStatement(
#                 effect=iam.Effect.ALLOW,
#                 actions=["iam:CreateServiceLinkedRole"],
#                 resources=["*"],
#                 conditions={
#                     "StringEquals": {
#                         "iam:AWSServiceName": [
#                             "replication.dynamodb.amazonaws.com",
#                             "dax.amazonaws.com",
#                             "dynamodb.application-autoscaling.amazonaws.com",
#                             "contributorinsights.dynamodb.amazonaws.com",
#                             "kinesisreplication.dynamodb.amazonaws.com"
#                         ]
#                     }
#                 }
#             )
#         )

#         # Add CloudWatch Logs permissions specific to this function
#         role.add_to_policy(
#             iam.PolicyStatement(
#                 effect=iam.Effect.ALLOW,
#                 actions=["logs:CreateLogGroup"],
#                 resources=[f"arn:aws:logs:us-east-1:{account_id}:*"]
#             )
#         )

#         role.add_to_policy(
#             iam.PolicyStatement(
#                 effect=iam.Effect.ALLOW,
#                 actions=[
#                     "logs:CreateLogStream",
#                     "logs:PutLogEvents"
#                 ],
#                 resources=[
#                     f"arn:aws:logs:us-east-1:{account_id}:log-group:/aws/lambda/query-analytics-backfill:*"
#                 ]
#             )
#         )

#     def add_query_analytics_api_role_policies(self, role, account_id):
#         role.add_to_policy(
#             iam.PolicyStatement(
#                 effect=iam.Effect.ALLOW,
#                 actions=[
#                     "dynamodb:DescribeStream",
#                     "dynamodb:GetRecords",
#                     "dynamodb:GetShardIterator",
#                     "dynamodb:ListStreams",
#                     "logs:CreateLogGroup",
#                     "logs:CreateLogStream",
#                     "logs:PutLogEvents"
#                 ],
#                 resources=["*"]
#             )
#         )

#         # Add DynamoDB full access
#         role.add_to_policy(
#             iam.PolicyStatement(
#                 actions=["dynamodb:*", "dax:*"],
#                 resources=["*"]
#             )
#         )

#         # Add various AWS service permissions for DynamoDB operations
#         role.add_to_policy(
#             iam.PolicyStatement(
#                 actions=[
#                     "application-autoscaling:DeleteScalingPolicy",
#                     "application-autoscaling:DeregisterScalableTarget",
#                     "application-autoscaling:DescribeScalableTargets",
#                     "application-autoscaling:DescribeScalingActivities",
#                     "application-autoscaling:DescribeScalingPolicies",
#                     "application-autoscaling:PutScalingPolicy",
#                     "application-autoscaling:RegisterScalableTarget",
#                     "cloudwatch:DeleteAlarms",
#                     "cloudwatch:DescribeAlarmHistory",
#                     "cloudwatch:DescribeAlarms",
#                     "cloudwatch:DescribeAlarmsForMetric",
#                     "cloudwatch:GetMetricStatistics",
#                     "cloudwatch:ListMetrics",
#                     "cloudwatch:PutMetricAlarm",
#                     "cloudwatch:GetMetricData",
#                     "datapipeline:ActivatePipeline",
#                     "datapipeline:CreatePipeline",
#                     "datapipeline:DeletePipeline",
#                     "datapipeline:DescribeObjects",
#                     "datapipeline:DescribePipelines",
#                     "datapipeline:GetPipelineDefinition",
#                     "datapipeline:ListPipelines",
#                     "datapipeline:PutPipelineDefinition",
#                     "datapipeline:QueryObjects",
#                     "ec2:DescribeVpcs",
#                     "ec2:DescribeSubnets",
#                     "ec2:DescribeSecurityGroups",
#                     "iam:GetRole",
#                     "iam:ListRoles",
#                     "kms:DescribeKey",
#                     "kms:ListAliases",
#                     "sns:CreateTopic",
#                     "sns:DeleteTopic",
#                     "sns:ListSubscriptions",
#                     "sns:ListSubscriptionsByTopic",
#                     "sns:ListTopics",
#                     "sns:Subscribe",
#                     "sns:Unsubscribe",
#                     "sns:SetTopicAttributes",
#                     "lambda:CreateFunction",
#                     "lambda:ListFunctions",
#                     "lambda:ListEventSourceMappings",
#                     "lambda:CreateEventSourceMapping",
#                     "lambda:DeleteEventSourceMapping",
#                     "lambda:GetFunctionConfiguration",
#                     "lambda:DeleteFunction",
#                     "resource-groups:ListGroups",
#                     "resource-groups:ListGroupResources",
#                     "resource-groups:GetGroup",
#                     "resource-groups:GetGroupQuery",
#                     "resource-groups:DeleteGroup",
#                     "resource-groups:CreateGroup",
#                     "tag:GetResources",
#                     "kinesis:ListStreams",
#                     "kinesis:DescribeStream",
#                     "kinesis:DescribeStreamSummary"
#                 ],
#                 resources=["*"]
#             )
#         )

#         # Add CloudWatch Insights access
#         role.add_to_policy(
#             iam.PolicyStatement(
#                 actions=["cloudwatch:GetInsightRuleReport"],
#                 resources=["arn:aws:cloudwatch:*:*:insight-rule/DynamoDBContributorInsights*"]
#             )
#         )

#         # Add IAM PassRole permissions
#         role.add_to_policy(
#             iam.PolicyStatement(
#                 actions=["iam:PassRole"],
#                 resources=["*"],
#                 conditions={
#                     "StringLike": {
#                         "iam:PassedToService": [
#                             "application-autoscaling.amazonaws.com",
#                             "application-autoscaling.amazonaws.com.cn",
#                             "dax.amazonaws.com"
#                         ]
#                     }
#                 }
#             )
#         )

#         # Add IAM CreateServiceLinkedRole permissions
#         role.add_to_policy(
#             iam.PolicyStatement(
#                 effect=iam.Effect.ALLOW,
#                 actions=["iam:CreateServiceLinkedRole"],
#                 resources=["*"],
#                 conditions={
#                     "StringEquals": {
#                         "iam:AWSServiceName": [
#                             "replication.dynamodb.amazonaws.com",
#                             "dax.amazonaws.com",
#                             "dynamodb.application-autoscaling.amazonaws.com",
#                             "contributorinsights.dynamodb.amazonaws.com",
#                             "kinesisreplication.dynamodb.amazonaws.com"
#                         ]
#                     }
#                 }
#             )
#         )

#         # Add CloudWatch Logs permissions specific to this function
#         role.add_to_policy(
#             iam.PolicyStatement(
#                 effect=iam.Effect.ALLOW,
#                 actions=["logs:CreateLogGroup"],
#                 resources=[f"arn:aws:logs:us-east-1:{account_id}:*"]
#             )
#         )

#         role.add_to_policy(
#             iam.PolicyStatement(
#                 effect=iam.Effect.ALLOW,
#                 actions=[
#                     "logs:CreateLogStream",
#                     "logs:PutLogEvents"
#                 ],
#                 resources=[
#                     f"arn:aws:logs:us-east-1:{account_id}:log-group:/aws/lambda/query-analytics-api:*"
#                 ]
#             )
#         )

#     def add_referrals_api_handler_role_policies(self, role, account_id):
#         role.add_to_policy(
#             iam.PolicyStatement(
#                 sid="CloudWatchLogsFullAccess",
#                 effect=iam.Effect.ALLOW,
#                 actions=[
#                     "logs:*",
#                     "cloudwatch:GenerateQuery"
#                 ],
#                 resources=["*"]
#             )
#         )

#         # Add Lambda basic execution permissions
#         role.add_to_policy(
#             iam.PolicyStatement(
#                 effect=iam.Effect.ALLOW,
#                 actions=[
#                     "logs:CreateLogGroup",
#                     "logs:CreateLogStream",
#                     "logs:PutLogEvents"
#                 ],
#                 resources=["*"]
#             )
#         )

#         # Add DynamoDB full access
#         role.add_to_policy(
#             iam.PolicyStatement(
#                 actions=["dynamodb:*", "dax:*"],
#                 resources=["*"]
#             )
#         )

#         # Add various AWS service permissions for DynamoDB operations
#         role.add_to_policy(
#             iam.PolicyStatement(
#                 actions=[
#                     "application-autoscaling:DeleteScalingPolicy",
#                     "application-autoscaling:DeregisterScalableTarget",
#                     "application-autoscaling:DescribeScalableTargets",
#                     "application-autoscaling:DescribeScalingActivities",
#                     "application-autoscaling:DescribeScalingPolicies",
#                     "application-autoscaling:PutScalingPolicy",
#                     "application-autoscaling:RegisterScalableTarget",
#                     "cloudwatch:DeleteAlarms",
#                     "cloudwatch:DescribeAlarmHistory",
#                     "cloudwatch:DescribeAlarms",
#                     "cloudwatch:DescribeAlarmsForMetric",
#                     "cloudwatch:GetMetricStatistics",
#                     "cloudwatch:ListMetrics",
#                     "cloudwatch:PutMetricAlarm",
#                     "cloudwatch:GetMetricData",
#                     "datapipeline:ActivatePipeline",
#                     "datapipeline:CreatePipeline",
#                     "datapipeline:DeletePipeline",
#                     "datapipeline:DescribeObjects",
#                     "datapipeline:DescribePipelines",
#                     "datapipeline:GetPipelineDefinition",
#                     "datapipeline:ListPipelines",
#                     "datapipeline:PutPipelineDefinition",
#                     "datapipeline:QueryObjects",
#                     "ec2:DescribeVpcs",
#                     "ec2:DescribeSubnets",
#                     "ec2:DescribeSecurityGroups",
#                     "iam:GetRole",
#                     "iam:ListRoles",
#                     "kms:DescribeKey",
#                     "kms:ListAliases",
#                     "sns:CreateTopic",
#                     "sns:DeleteTopic",
#                     "sns:ListSubscriptions",
#                     "sns:ListSubscriptionsByTopic",
#                     "sns:ListTopics",
#                     "sns:Subscribe",
#                     "sns:Unsubscribe",
#                     "sns:SetTopicAttributes",
#                     "lambda:CreateFunction",
#                     "lambda:ListFunctions",
#                     "lambda:ListEventSourceMappings",
#                     "lambda:CreateEventSourceMapping",
#                     "lambda:DeleteEventSourceMapping",
#                     "lambda:GetFunctionConfiguration",
#                     "lambda:DeleteFunction",
#                     "resource-groups:ListGroups",
#                     "resource-groups:ListGroupResources",
#                     "resource-groups:GetGroup",
#                     "resource-groups:GetGroupQuery",
#                     "resource-groups:DeleteGroup",
#                     "resource-groups:CreateGroup",
#                     "tag:GetResources",
#                     "kinesis:ListStreams",
#                     "kinesis:DescribeStream",
#                     "kinesis:DescribeStreamSummary"
#                 ],
#                 resources=["*"]
#             )
#         )

#         # Add CloudWatch Insights access
#         role.add_to_policy(
#             iam.PolicyStatement(
#                 actions=["cloudwatch:GetInsightRuleReport"],
#                 resources=["arn:aws:cloudwatch:*:*:insight-rule/DynamoDBContributorInsights*"]
#             )
#         )

#         # Add IAM PassRole permissions
#         role.add_to_policy(
#             iam.PolicyStatement(
#                 actions=["iam:PassRole"],
#                 resources=["*"],
#                 conditions={
#                     "StringLike": {
#                         "iam:PassedToService": [
#                             "application-autoscaling.amazonaws.com",
#                             "application-autoscaling.amazonaws.com.cn",
#                             "dax.amazonaws.com"
#                         ]
#                     }
#                 }
#             )
#         )

#         # Add IAM CreateServiceLinkedRole permissions
#         role.add_to_policy(
#             iam.PolicyStatement(
#                 effect=iam.Effect.ALLOW,
#                 actions=["iam:CreateServiceLinkedRole"],
#                 resources=["*"],
#                 conditions={
#                     "StringEquals": {
#                         "iam:AWSServiceName": [
#                             "replication.dynamodb.amazonaws.com",
#                             "dax.amazonaws.com",
#                             "dynamodb.application-autoscaling.amazonaws.com",
#                             "contributorinsights.dynamodb.amazonaws.com",
#                             "kinesisreplication.dynamodb.amazonaws.com"
#                         ]
#                     }
#                 }
#             )
#         )

#         # Inline policy: cloudWatchLogs
#         role.add_to_policy(
#             iam.PolicyStatement(
#                 effect=iam.Effect.ALLOW,
#                 actions=[
#                     "logs:CreateLogGroup",
#                     "logs:CreateLogStream",
#                     "logs:PutLogEvents"
#                 ],
#                 resources=["arn:aws:logs:*:*:*"]
#             )
#         )

#         # Inline policy: DynamoDBReferralsAccess
#         role.add_to_policy(
#             iam.PolicyStatement(
#                 effect=iam.Effect.ALLOW,
#                 actions=[
#                     "dynamodb:PutItem",
#                     "dynamodb:GetItem",
#                     "dynamodb:UpdateItem",
#                     "dynamodb:DeleteItem",
#                     "dynamodb:Scan",
#                     "dynamodb:Query"
#                 ],
#                 resources=["arn:aws:dynamodb:*:*:table/Referrals"]
#             )
#         )

#         # Inline policy: lambdaWebSocketPolicy
#         role.add_to_policy(
#             iam.PolicyStatement(
#                 effect=iam.Effect.ALLOW,
#                 actions=["execute-api:ManageConnections"],
#                 resources=["arn:aws:execute-api:*:*:*/*/POST/@connections/*"]
#             )
#         )

#         role.add_to_policy(
#             iam.PolicyStatement(
#                 effect=iam.Effect.ALLOW,
#                 actions=[
#                     "dynamodb:PutItem",
#                     "dynamodb:GetItem",
#                     "dynamodb:DeleteItem",
#                     "dynamodb:Scan"
#                 ],
#                 resources=["arn:aws:dynamodb:*:*:table/WebSocketConnections"]
#             )
#         )

#         # Inline policy: referralDDBAccess
#         role.add_to_policy(
#             iam.PolicyStatement(
#                 effect=iam.Effect.ALLOW,
#                 actions=[
#                     "dynamodb:GetItem",
#                     "dynamodb:Query",
#                     "dynamodb:Scan"
#                 ],
#                 resources=[f"arn:aws:dynamodb:us-east-1:{account_id}:table/referral_data"]
#             )
#         )

#     def add_sms_chat_integration_role_policies(self, role, account_id):
#         """Add all necessary policies to the smsChatIntegration role"""

#         # Add API Gateway full access
#         role.add_to_policy(
#             iam.PolicyStatement(
#                 effect=iam.Effect.ALLOW,
#                 actions=["apigateway:*"],
#                 resources=["arn:aws:apigateway:*::/*"]
#             )
#         )

#         # Add SNS full access
#         role.add_to_policy(
#             iam.PolicyStatement(
#                 sid="SNSFullAccess",
#                 effect=iam.Effect.ALLOW,
#                 actions=["sns:*"],
#                 resources=["*"]
#             )
#         )

#         # Add SMS access via SNS
#         role.add_to_policy(
#             iam.PolicyStatement(
#                 sid="SMSAccessViaSNS",
#                 effect=iam.Effect.ALLOW,
#                 actions=[
#                     "sms-voice:DescribeVerifiedDestinationNumbers",
#                     "sms-voice:CreateVerifiedDestinationNumber",
#                     "sms-voice:SendDestinationNumberVerificationCode",
#                     "sms-voice:SendTextMessage",
#                     "sms-voice:DeleteVerifiedDestinationNumber",
#                     "sms-voice:VerifyDestinationNumber",
#                     "sms-voice:DescribeAccountAttributes",
#                     "sms-voice:DescribeSpendLimits",
#                     "sms-voice:DescribePhoneNumbers",
#                     "sms-voice:SetTextMessageSpendLimitOverride",
#                     "sms-voice:DescribeOptedOutNumbers",
#                     "sms-voice:DeleteOptedOutNumber"
#                 ],
#                 resources=["*"],
#                 conditions={
#                     "StringEquals": {
#                         "aws:CalledViaLast": "sns.amazonaws.com"
#                     }
#                 }
#             )
#         )

#         # Add Execute API permissions
#         role.add_to_policy(
#             iam.PolicyStatement(
#                 effect=iam.Effect.ALLOW,
#                 actions=[
#                     "execute-api:Invoke",
#                     "execute-api:ManageConnections"
#                 ],
#                 resources=["arn:aws:execute-api:*:*:*"]
#             )
#         )

#         # Add DynamoDB and related services access
#         role.add_to_policy(
#             iam.PolicyStatement(
#                 actions=[
#                     "dynamodb:*",
#                     "dax:*",
#                     "application-autoscaling:DeleteScalingPolicy",
#                     "application-autoscaling:DeregisterScalableTarget",
#                     "application-autoscaling:DescribeScalableTargets",
#                     "application-autoscaling:DescribeScalingActivities",
#                     "application-autoscaling:DescribeScalingPolicies",
#                     "application-autoscaling:PutScalingPolicy",
#                     "application-autoscaling:RegisterScalableTarget",
#                     "cloudwatch:DeleteAlarms",
#                     "cloudwatch:DescribeAlarmHistory",
#                     "cloudwatch:DescribeAlarms",
#                     "cloudwatch:DescribeAlarmsForMetric",
#                     "cloudwatch:GetMetricStatistics",
#                     "cloudwatch:ListMetrics",
#                     "cloudwatch:PutMetricAlarm",
#                     "cloudwatch:GetMetricData",
#                     "datapipeline:ActivatePipeline",
#                     "datapipeline:CreatePipeline",
#                     "datapipeline:DeletePipeline",
#                     "datapipeline:DescribeObjects",
#                     "datapipeline:DescribePipelines",
#                     "datapipeline:GetPipelineDefinition",
#                     "datapipeline:ListPipelines",
#                     "datapipeline:PutPipelineDefinition",
#                     "datapipeline:QueryObjects",
#                     "ec2:DescribeVpcs",
#                     "ec2:DescribeSubnets",
#                     "ec2:DescribeSecurityGroups",
#                     "iam:GetRole",
#                     "iam:ListRoles",
#                     "kms:DescribeKey",
#                     "kms:ListAliases",
#                     "sns:CreateTopic",
#                     "sns:DeleteTopic",
#                     "sns:ListSubscriptions",
#                     "sns:ListSubscriptionsByTopic",
#                     "sns:ListTopics",
#                     "sns:Subscribe",
#                     "sns:Unsubscribe",
#                     "sns:SetTopicAttributes",
#                     "lambda:CreateFunction",
#                     "lambda:ListFunctions",
#                     "lambda:ListEventSourceMappings",
#                     "lambda:CreateEventSourceMapping",
#                     "lambda:DeleteEventSourceMapping",
#                     "lambda:GetFunctionConfiguration",
#                     "lambda:DeleteFunction",
#                     "resource-groups:ListGroups",
#                     "resource-groups:ListGroupResources",
#                     "resource-groups:GetGroup",
#                     "resource-groups:GetGroupQuery",
#                     "resource-groups:DeleteGroup",
#                     "resource-groups:CreateGroup",
#                     "tag:GetResources",
#                     "kinesis:ListStreams",
#                     "kinesis:DescribeStream",
#                     "kinesis:DescribeStreamSummary"
#                 ],
#                 resources=["*"]
#             )
#         )

#         # Add CloudWatch Insights access
#         role.add_to_policy(
#             iam.PolicyStatement(
#                 actions=["cloudwatch:GetInsightRuleReport"],
#                 resources=["arn:aws:cloudwatch:*:*:insight-rule/DynamoDBContributorInsights*"]
#             )
#         )

#         # Add IAM PassRole permissions
#         role.add_to_policy(
#             iam.PolicyStatement(
#                 actions=["iam:PassRole"],
#                 resources=["*"],
#                 conditions={
#                     "StringLike": {
#                         "iam:PassedToService": [
#                             "application-autoscaling.amazonaws.com",
#                             "application-autoscaling.amazonaws.com.cn",
#                             "dax.amazonaws.com"
#                         ]
#                     }
#                 }
#             )
#         )

#         # Add IAM CreateServiceLinkedRole permissions
#         role.add_to_policy(
#             iam.PolicyStatement(
#                 effect=iam.Effect.ALLOW,
#                 actions=["iam:CreateServiceLinkedRole"],
#                 resources=["*"],
#                 conditions={
#                     "StringEquals": {
#                         "iam:AWSServiceName": [
#                             "replication.dynamodb.amazonaws.com",
#                             "dax.amazonaws.com",
#                             "dynamodb.application-autoscaling.amazonaws.com",
#                             "contributorinsights.dynamodb.amazonaws.com",
#                             "kinesisreplication.dynamodb.amazonaws.com"
#                         ]
#                     }
#                 }
#             )
#         )

#         # Add CloudWatch Logs permissions
#         role.add_to_policy(
#             iam.PolicyStatement(
#                 effect=iam.Effect.ALLOW,
#                 actions=["logs:CreateLogGroup"],
#                 resources=[f"arn:aws:logs:us-east-1:{account_id}:*"]
#             )
#         )

#         role.add_to_policy(
#             iam.PolicyStatement(
#                 effect=iam.Effect.ALLOW,
#                 actions=[
#                     "logs:CreateLogStream",
#                     "logs:PutLogEvents"
#                 ],
#                 resources=[
#                     f"arn:aws:logs:us-east-1:{account_id}:log-group:/aws/lambda/smsChatIntegration:*"
#                 ]
#             )
#         )

#         # Inline policy: smsCrossAccountPermission
#         role.add_to_policy(
#             iam.PolicyStatement(
#                 effect=iam.Effect.ALLOW,
#                 actions=["sts:AssumeRole"],
#                 resources=["arn:aws:iam::514811724234:role/crossAccountPinpointAccess"]
#             )
#         )

#     def add_query_analytics_stream_processor_role_policies(self, role, account_id):
#         role.add_to_policy(
#             iam.PolicyStatement(
#                 effect=iam.Effect.ALLOW,
#                 actions=[
#                     "dynamodb:DescribeStream",
#                     "dynamodb:GetRecords",
#                     "dynamodb:GetShardIterator",
#                     "dynamodb:ListStreams",
#                     "logs:CreateLogGroup",
#                     "logs:CreateLogStream",
#                     "logs:PutLogEvents"
#                 ],
#                 resources=["*"]
#             )
#         )

#         # Add DynamoDB full access and related services
#         role.add_to_policy(
#             iam.PolicyStatement(
#                 actions=[
#                     "dynamodb:*",
#                     "dax:*",
#                     "application-autoscaling:DeleteScalingPolicy",
#                     "application-autoscaling:DeregisterScalableTarget",
#                     "application-autoscaling:DescribeScalableTargets",
#                     "application-autoscaling:DescribeScalingActivities",
#                     "application-autoscaling:DescribeScalingPolicies",
#                     "application-autoscaling:PutScalingPolicy",
#                     "application-autoscaling:RegisterScalableTarget",
#                     "cloudwatch:DeleteAlarms",
#                     "cloudwatch:DescribeAlarmHistory",
#                     "cloudwatch:DescribeAlarms",
#                     "cloudwatch:DescribeAlarmsForMetric",
#                     "cloudwatch:GetMetricStatistics",
#                     "cloudwatch:ListMetrics",
#                     "cloudwatch:PutMetricAlarm",
#                     "cloudwatch:GetMetricData",
#                     "datapipeline:ActivatePipeline",
#                     "datapipeline:CreatePipeline",
#                     "datapipeline:DeletePipeline",
#                     "datapipeline:DescribeObjects",
#                     "datapipeline:DescribePipelines",
#                     "datapipeline:GetPipelineDefinition",
#                     "datapipeline:ListPipelines",
#                     "datapipeline:PutPipelineDefinition",
#                     "datapipeline:QueryObjects",
#                     "ec2:DescribeVpcs",
#                     "ec2:DescribeSubnets",
#                     "ec2:DescribeSecurityGroups",
#                     "iam:GetRole",
#                     "iam:ListRoles",
#                     "kms:DescribeKey",
#                     "kms:ListAliases",
#                     "sns:CreateTopic",
#                     "sns:DeleteTopic",
#                     "sns:ListSubscriptions",
#                     "sns:ListSubscriptionsByTopic",
#                     "sns:ListTopics",
#                     "sns:Subscribe",
#                     "sns:Unsubscribe",
#                     "sns:SetTopicAttributes",
#                     "lambda:CreateFunction",
#                     "lambda:ListFunctions",
#                     "lambda:ListEventSourceMappings",
#                     "lambda:CreateEventSourceMapping",
#                     "lambda:DeleteEventSourceMapping",
#                     "lambda:GetFunctionConfiguration",
#                     "lambda:DeleteFunction",
#                     "resource-groups:ListGroups",
#                     "resource-groups:ListGroupResources",
#                     "resource-groups:GetGroup",
#                     "resource-groups:GetGroupQuery",
#                     "resource-groups:DeleteGroup",
#                     "resource-groups:CreateGroup",
#                     "tag:GetResources",
#                     "kinesis:ListStreams",
#                     "kinesis:DescribeStream",
#                     "kinesis:DescribeStreamSummary"
#                 ],
#                 resources=["*"]
#             )
#         )

#         # Add CloudWatch Insights access
#         role.add_to_policy(
#             iam.PolicyStatement(
#                 actions=["cloudwatch:GetInsightRuleReport"],
#                 resources=["arn:aws:cloudwatch:*:*:insight-rule/DynamoDBContributorInsights*"]
#             )
#         )

#         # Add IAM PassRole permissions
#         role.add_to_policy(
#             iam.PolicyStatement(
#                 actions=["iam:PassRole"],
#                 resources=["*"],
#                 conditions={
#                     "StringLike": {
#                         "iam:PassedToService": [
#                             "application-autoscaling.amazonaws.com",
#                             "application-autoscaling.amazonaws.com.cn",
#                             "dax.amazonaws.com"
#                         ]
#                     }
#                 }
#             )
#         )

#         # Add IAM CreateServiceLinkedRole permissions
#         role.add_to_policy(
#             iam.PolicyStatement(
#                 effect=iam.Effect.ALLOW,
#                 actions=["iam:CreateServiceLinkedRole"],
#                 resources=["*"],
#                 conditions={
#                     "StringEquals": {
#                         "iam:AWSServiceName": [
#                             "replication.dynamodb.amazonaws.com",
#                             "dax.amazonaws.com",
#                             "dynamodb.application-autoscaling.amazonaws.com",
#                             "contributorinsights.dynamodb.amazonaws.com",
#                             "kinesisreplication.dynamodb.amazonaws.com"
#                         ]
#                     }
#                 }
#             )
#         )

#         # Add CloudWatch Logs permissions specific to this function
#         role.add_to_policy(
#             iam.PolicyStatement(
#                 effect=iam.Effect.ALLOW,
#                 actions=["logs:CreateLogGroup"],
#                 resources=[f"arn:aws:logs:us-east-1:{account_id}:*"]
#             )
#         )

#         role.add_to_policy(
#             iam.PolicyStatement(
#                 effect=iam.Effect.ALLOW,
#                 actions=[
#                     "logs:CreateLogStream",
#                     "logs:PutLogEvents"
#                 ],
#                 resources=[
#                     f"arn:aws:logs:us-east-1:{account_id}:log-group:/aws/lambda/query-analytics-stream-processor:*"
#                 ]
#             )
#         )