from aws_cdk import (
    # Duration,
    aws_s3 as s3, aws_iam as iam, aws_ec2 as ec2,
    NestedStack, RemovalPolicy, CfnOutput, )
from constructs import Construct


class ServerAuthorization(NestedStack):

    def __init__(self, scope: Construct, construct_id: str,
                 vpc: ec2.IVpc,
                 removal_policy: RemovalPolicy = RemovalPolicy.RETAIN,
                 **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)

        role = iam.Role(self, "Squad44ServerRole", role_name="Squad44ServerRole",
                        assumed_by=iam.ServicePrincipal("ec2.amazonaws.com"))
        # role.add_managed_policy(iam.ManagedPolicy.from_aws_managed_policy_name(
        #     "AmazonSSMManagedInstanceCore"))
        # role.add_managed_policy(iam.ManagedPolicy.from_aws_managed_policy_name(
        #     "EC2InstanceProfileForImageBuilder"))
        role.apply_removal_policy(removal_policy)

        # create an instance profile to attach the role
        self.instance_profile = iam.InstanceProfile(self,
                                                    "Squad44ServerInstanceProfile",
                                                    instance_profile_name="Squad44ServerInstanceProfile",
                                                    role=role)
        self.instance_profile.apply_removal_policy(removal_policy)

        CfnOutput(self, "InstanceProfileName",
                  value=self.instance_profile.instance_profile_name,)
        CfnOutput(self, "InstanceProfileArn",
                  value=self.instance_profile.instance_profile_arn,)

        self.security_group = ec2.SecurityGroup(self, "Squad44ServerSecurityGroup",
                                                allow_all_outbound=False,
                                                vpc=vpc,
                                                )
        CfnOutput(self, "SecurityGroupId", value=self.security_group.security_group_id,
                  description='The ID of the Security Group.')

        self.key_pair = ec2.KeyPair(self, "KeyPair",
                                    type=ec2.KeyPairType.ED25519,
                                    format=ec2.KeyPairFormat.PEM,
                                    )
        self.key_pair.apply_removal_policy(removal_policy)

        CfnOutput(self, "KeyPairName", value=self.key_pair.key_pair_name,
                  description="The unique name of the key pair.")
        CfnOutput(self, "KeyPairId", value=self.key_pair.key_pair_id,
                  description="The unique ID of the key pair.")
        CfnOutput(self, "KeyPairFingerprint", value=self.key_pair.key_pair_fingerprint,
                  description="The fingerprint of the key pair.")
