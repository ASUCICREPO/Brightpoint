#!/usr/bin/env python3
import os
import sys
import aws_cdk as cdk
import boto3
from brightpoint.brightpoint_stack import BrightpointStack

app = cdk.App()

# Get environment from context
env_name = app.node.try_get_context("env") or os.environ.get("CDK_ENV", "dev")

# Get AWS profile from context
aws_profile = app.node.try_get_context("profile") or os.environ.get("CDK_PROFILE", "Sandbox2025")

# Get account and region from context or use the AWS profile
account_id = app.node.try_get_context("account")
region = app.node.try_get_context("region") or "us-east-1"

# If account_id is not provided in context, try to get it from the profile
if not account_id and aws_profile:
    try:
        session = boto3.Session(profile_name=aws_profile)
        account_id = session.client('sts').get_caller_identity()["Account"]
        if not region and session.region_name:
            region = session.region_name
    except Exception as e:
        print(f"Warning: Could not get account ID from profile {aws_profile}: {e}")

# Validate environment
valid_envs = ["dev", "test", "prod"]
if env_name not in valid_envs:
    print(f"Error: Invalid environment '{env_name}'. Must be one of: {valid_envs}")
    sys.exit(1)

print(f"Deploying to account {account_id} in region {region} for environment {env_name}")

# Create environment using detected values
env = cdk.Environment(
    account=account_id,
    region=region
)

# Create stack with environment-specific name
stack_name = f"BrightpointStack-{env_name}"
BrightpointStack(
    app,
    stack_name,
    env_name=env_name,
    env=env,
    description=f"Brightpoint Referral Chatbot infrastructure - {env_name}"
)

app.synth()