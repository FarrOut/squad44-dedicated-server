#!/usr/bin/env python3
import os

from aws_cdk import (
    Duration, App, Environment,
    aws_s3 as s3, aws_iam as iam, aws_ec2 as ec2,
    NestedStack, RemovalPolicy, CfnOutput, )
from squad44_dedicated_server.building import squad44_image_builder_stack
from squad44_dedicated_server.squad44_server_stack import Squad44Server

from squad44_dedicated_server.building.squad44_image_builder_stack import Squad44ImageBuilder
from squad44_dedicated_server.monitoring.watchdog_stack_squad44 import WatchdogStack


default_env = Environment(account=os.getenv(
    'CDK_DEFAULT_ACCOUNT'), region=os.getenv('CDK_DEFAULT_REGION'))
africa_env = Environment(account=os.getenv(
    'CDK_DEFAULT_ACCOUNT'), region='af-south-1')

app = App()

version = "0.0.37"

peers = app.node.try_get_context("peers")
key_name = app.node.try_get_context("key_name")

image_builder = Squad44ImageBuilder(app, "Squad44ImageBuilder",
                                    env=africa_env,
                                    version=version,
                                    removal_policy=RemovalPolicy.DESTROY,
                                    )

Squad44Server(app, "Squad44Server",
              env=africa_env,
              whitelisted_peer=ec2.Peer.prefix_list(peers),
              key_name=key_name,
              removal_policy=RemovalPolicy.DESTROY,
              )

WatchdogStack(app, "WatchdogSquad44",
              env=africa_env,
              removal_policy=RemovalPolicy.DESTROY,
              )

app.synth()
