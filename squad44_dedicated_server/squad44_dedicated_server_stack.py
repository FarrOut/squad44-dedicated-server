from aws_cdk import (
    # Duration,
    Stack, RemovalPolicy,
    # aws_sqs as sqs,
)
from constructs import Construct
from squad44_dedicated_server.storage.s3_stack import S3NestedStack


class Squad44DedicatedServerStack(Stack):

    def __init__(self, scope: Construct, construct_id: str,
                 removal_policy: RemovalPolicy = RemovalPolicy.DESTROY,
                 **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)

        bucket = S3NestedStack(
            self, "S3NestedStack", auto_delete_objects=True, removal_policy=RemovalPolicy.DESTROY).bucket
        
        
