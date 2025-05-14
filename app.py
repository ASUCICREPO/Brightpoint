#!/usr/bin/env python3
import os
import sys
import aws_cdk as cdk

from brightpoint.brightpoint_stack import BrightpointStack

app = cdk.App()

# Get environment from command line or context
env_name = app.node.try_get_context("env") or os.environ.get("CDK_ENV", "dev")

# Validate environment
valid_envs = ["dev", "test", "prod"]
if env_name not in valid_envs:
    print(f"Error: Invalid environment '{env_name}'. Must be one of: {valid_envs}")
    sys.exit(1)

# Using Brightpoint Sandbox account
env = cdk.Environment(
    account="216989103356",
    region="us-east-1"
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