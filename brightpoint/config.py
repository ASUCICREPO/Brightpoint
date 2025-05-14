# brightpoint/config.py
from aws_cdk import aws_dynamodb as dynamodb, aws_apigateway as apigateway, RemovalPolicy

class EnvironmentConfig:
    """Environment-specific configuration for Brightpoint Stack"""

    CONFIGS = {
        "dev": {
            "memory_size": {
                "referralChatbotLambda": 1024,
                "perplexityLambda": 1024,
                "ProcessUserData": 1024,
                "query-analytics-api": 512,
                "ReferralsApiHandler": 512,
            },
            "timeout": {
                "referralChatbotLambda": 300,
                "perplexityLambda": 300,
                "ProcessUserData": 300,
                "query-analytics-api": 120,
                "ReferralsApiHandler": 120,
            },
            "table_settings": {
                "billing_mode": dynamodb.BillingMode.PAY_PER_REQUEST,
                "removal_policy": RemovalPolicy.DESTROY,
            },
            "api_settings": {
                "logging_level": apigateway.MethodLoggingLevel.INFO,
                "data_trace_enabled": True,
                "metrics_enabled": True,
            }
        },
        "test": {
            "memory_size": {
                "referralChatbotLambda": 1024,
                "perplexityLambda": 2048,
                "ProcessUserData": 1024,
                "query-analytics-api": 1024,
                "ReferralsApiHandler": 1024,
            },
            "timeout": {
                "referralChatbotLambda": 600,
                "perplexityLambda": 600,
                "ProcessUserData": 600,
                "query-analytics-api": 300,
                "ReferralsApiHandler": 300,
            },
            "table_settings": {
                "billing_mode": dynamodb.BillingMode.PAY_PER_REQUEST,
                "removal_policy": RemovalPolicy.RETAIN,
            },
            "api_settings": {
                "logging_level": apigateway.MethodLoggingLevel.INFO,
                "data_trace_enabled": True,
                "metrics_enabled": True,
            }
        },
        "prod": {
            "memory_size": {
                "referralChatbotLambda": 2048,
                "perplexityLambda": 3008,
                "ProcessUserData": 2048,
                "query-analytics-api": 2048,
                "ReferralsApiHandler": 2048,
            },
            "timeout": {
                "referralChatbotLambda": 900,
                "perplexityLambda": 900,
                "ProcessUserData": 900,
                "query-analytics-api": 300,
                "ReferralsApiHandler": 300,
            },
            "table_settings": {
                "billing_mode": dynamodb.BillingMode.PAY_PER_REQUEST,
                "removal_policy": RemovalPolicy.RETAIN,
            },
            "api_settings": {
                "logging_level": apigateway.MethodLoggingLevel.ERROR,
                "data_trace_enabled": False,
                "metrics_enabled": True,
            }
        }
    }

    @classmethod
    def get_config(cls, env_name: str):
        """Get configuration for specified environment"""
        return cls.CONFIGS.get(env_name, cls.CONFIGS["dev"])