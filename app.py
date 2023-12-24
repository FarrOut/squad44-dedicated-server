#!/usr/bin/env python3
import os

import aws_cdk as cdk

from squad44_dedicated_server.squad44_dedicated_server_stack import Squad44DedicatedServerStack


default_env = cdk.Environment(account=os.getenv(
    'CDK_DEFAULT_ACCOUNT'), region=os.getenv('CDK_DEFAULT_REGION'))
africa_env = cdk.Environment(account=os.getenv(
    'CDK_DEFAULT_ACCOUNT'), region='af-south-1')

app = cdk.App()
Squad44DedicatedServerStack(app, "Squad44DedicatedServerStack",
                            env=africa_env,
                            removal_policy=cdk.RemovalPolicy.DESTROY,
                            )

app.synth()
