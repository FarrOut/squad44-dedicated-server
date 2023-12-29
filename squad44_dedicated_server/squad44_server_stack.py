from aws_cdk import (
    # Duration,
    Stack, RemovalPolicy, CfnOutput, aws_iam as iam,
    aws_ec2 as ec2, aws_autoscaling as autoscaling,
)
from constructs import Construct
from squad44_dedicated_server.deploying.networking.vpc_nestedstack import Vpc
from squad44_dedicated_server.deploying.security.server_authorization_nestedstack import ServerAuthorization
from squad44_dedicated_server.storage.build_assets_nestedstack import BuildAssetsNestedStack
from squad44_dedicated_server.storage.s3_nestedstack import S3NestedStack


class Squad44Server(Stack):

    def __init__(self, scope: Construct, construct_id: str,
                 #  machine_image: ec2.IMachineImage,
                 removal_policy: RemovalPolicy = RemovalPolicy.DESTROY,
                 **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)

        vpc = Vpc(self, "Vpc", removal_policy=removal_policy).vpc
        auth_stack = ServerAuthorization(
            self, "ServerAuthorization",
            vpc=vpc,
            removal_policy=removal_policy)
        security_group = auth_stack.security_group

        key_pair = auth_stack.key_pair
        CfnOutput(self, "KeyPairRetrievalCommand", value=f"aws ssm get-parameter --name /ec2/keypair/{key_pair.key_pair_id} --with-decryption --query Parameter.Value --output text > squad44-key-pair.pem",
                  description="The command to fetch the generated private key from the Parameter Store to a local file.")

        # COMPUTING

        machine_image = ec2.MachineImage.lookup(
            name='*squad44*', owners=[str(self.account)])

        # CfnOutput(self, "MachineImageId", value=str(machine_image),
        #           description='The ID of the Machine Image.')
        # CfnOutput(self, "MachineImageName", value=str(machine_image.image_name),
        #           description='The name of the Machine Image.')
        # CfnOutput(self, "MachineImageOwner", value=str(
        #     machine_image.image_owner_alias))

        # template = ec2.LaunchTemplate(self, "LaunchTemplate",
        #                               machine_image=machine_image,
        #                               security_group=security_group,
        #                               key_pair=key_pair,
        #                               instance_profile=auth_stack.instance_profile,
        #                               )
        # template.apply_removal_policy(removal_policy)

        # CfnOutput(self, "LaunchTemplateName", value=str(template.launch_template_name),
        #           description='The name of the Launch Template.')
        # CfnOutput(self, "LaunchTemplateId", value=str(template.launch_template_id),
        #           description='The ID of the Launch Template.')
        # CfnOutput(self, "LaunchTemplateDefaultVersionNumber", value=str(
        #     template.default_version_number), description='The default version for the launch template.')
