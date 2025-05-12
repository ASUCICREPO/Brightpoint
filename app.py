#!/usr/bin/env python3
import os
import aws_cdk as cdk
from brightpoint.brightpoint_stack import BrightpointStack

app = cdk.App()
BrightpointStack(app, "BrightpointStack",
    # If you have specific environment values:
    env=cdk.Environment(account=os.getenv('CDK_DEFAULT_ACCOUNT'), region="us-east-1"),
    description="Brightpoint Referral Chatbot infrastructure"
)

app.synth()