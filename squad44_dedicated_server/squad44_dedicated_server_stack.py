from aws_cdk import (
    # Duration,
    Stack, RemovalPolicy,
    # aws_sqs as sqs,
)
from constructs import Construct
from squad44_dedicated_server.images.image_builder_pipeline_nestedstack import ImageBuilderPipeline
from squad44_dedicated_server.security.authorization_nestedstack import AuthorizationNestedStack
from squad44_dedicated_server.storage.build_assets_nestedstack import BuildAssetsNestedStack
from squad44_dedicated_server.storage.s3_nestedstack import S3NestedStack


class Squad44DedicatedServerStack(Stack):

    def __init__(self, scope: Construct, construct_id: str,
                 removal_policy: RemovalPolicy = RemovalPolicy.DESTROY,
                 **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)

        # s3 prefix/key for storing components
        components_prefix = "components"

        bucket = S3NestedStack(
            self, "S3NestedStack", auto_delete_objects=True, removal_policy=removal_policy).bucket

        assets_stack = BuildAssetsNestedStack(
            self, "BuildAssetsNestedStack", bucket=bucket, components_prefix=components_prefix)

        instance_profile = AuthorizationNestedStack(
            self, 'AuthorizationNestedStack', removal_policy=removal_policy).instance_profile

        ImageBuilderPipeline(self, "ImageBuilderPipeline",
                             base_image_arn=f'arn:aws:imagebuilder:{
                                 self.region}:aws:image/amazon-linux-2023-arm64/2023.12.15',
                             image_pipeline_name='squad44-dedicated-server',
                             bucket_name=bucket.bucket_name,
                             components_prefix=components_prefix,
                             instance_profile=instance_profile,
                             ).add_dependency(assets_stack)
