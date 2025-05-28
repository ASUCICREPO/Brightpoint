from aws_cdk import (
    Stack,
    aws_dynamodb as dynamodb,
    RemovalPolicy,
    CfnOutput
)
from constructs import Construct

class DynamoDBTablesStack(Stack):
    def __init__(self, scope: Construct, construct_id: str, **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)

        # Table: WebSocketConnections
        websocket_connections_table = dynamodb.Table(
            self, 'WebSocketConnectionsTable',
            table_name='WebSocketConnections',
            partition_key=dynamodb.Attribute(name='connectionId', type=dynamodb.AttributeType.STRING),
            billing_mode=dynamodb.BillingMode.PAY_PER_REQUEST,
            removal_policy=RemovalPolicy.RETAIN,
        )

        # Table: perplexity_query_cache
        perplexity_query_cache_table = dynamodb.Table(
            self, 'perplexity_query_cacheTable',
            table_name='perplexity_query_cache',
            partition_key=dynamodb.Attribute(name='query_id', type=dynamodb.AttributeType.STRING),
            billing_mode=dynamodb.BillingMode.PAY_PER_REQUEST,
            removal_policy=RemovalPolicy.RETAIN,
        )

        # Table: query_analytics
        query_analytics_table = dynamodb.Table(
            self, 'query_analyticsTable',
            table_name='query_analytics',
            partition_key=dynamodb.Attribute(name='query_text', type=dynamodb.AttributeType.STRING),
            sort_key=dynamodb.Attribute(name='Zipcode', type=dynamodb.AttributeType.STRING),
            billing_mode=dynamodb.BillingMode.PAY_PER_REQUEST,
            removal_policy=RemovalPolicy.RETAIN,
        )

        # Table: referral_data
        referral_data_table = dynamodb.Table(
            self, 'referral_dataTable',
            table_name='referral_data',
            partition_key=dynamodb.Attribute(name='referral_id', type=dynamodb.AttributeType.STRING),
            billing_mode=dynamodb.BillingMode.PAY_PER_REQUEST,
            removal_policy=RemovalPolicy.RETAIN,
        )

        # Table: user_data
        user_data_table = dynamodb.Table(
            self, 'user_dataTable',
            table_name='user_data',
            partition_key=dynamodb.Attribute(name='user_id', type=dynamodb.AttributeType.STRING),
            billing_mode=dynamodb.BillingMode.PAY_PER_REQUEST,
            stream=dynamodb.StreamViewType.NEW_AND_OLD_IMAGES,
            removal_policy=RemovalPolicy.RETAIN,
        )

        # Output the DynamoDB table names
        CfnOutput(
            self, "WebSocketConnectionsTableName",
            value=websocket_connections_table.table_name,
            description="WebSocket Connections Table Name"
        )

        CfnOutput(
            self, "PerplexityQueryCacheTableName",
            value=perplexity_query_cache_table.table_name,
            description="Perplexity Query Cache Table Name"
        )

        CfnOutput(
            self, "QueryAnalyticsTableName",
            value=query_analytics_table.table_name,
            description="Query Analytics Table Name"
        )

        CfnOutput(
            self, "ReferralDataTableName",
            value=referral_data_table.table_name,
            description="Referral Data Table Name"
        )

        CfnOutput(
            self, "UserDataTableName",
            value=user_data_table.table_name,
            description="User Data Table Name"
        )