from aws_cdk import (
    # Duration,
    aws_s3 as s3, aws_imagebuilder as imagebuilder,
    aws_iam as iam,
    NestedStack, RemovalPolicy, CfnOutput, )
from constructs import Construct
import time
import uuid


class ImageBuilderPipeline(NestedStack):

    def __init__(self, scope: Construct, construct_id: str,
                 version: str,
                 bucket_name: str,
                 components_prefix: str,
                 base_image_arn: str,
                 image_pipeline_name: str,
                 instance_profile: iam.IInstanceProfile,
                 distribution_configuration: imagebuilder.CfnDistributionConfiguration,
                 removal_policy: RemovalPolicy = RemovalPolicy.RETAIN,
                 **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)

        bucket_uri = "s3://" + bucket_name + "/" + components_prefix

        # [Server Hosting] How to set up a dedicated server.
        # https://steamcommunity.com/app/736220/discussions/0/2967271684632425013/

        # NOTE: when creating components, version number is supplied manually. If you update the components yaml and
        # need a new version deployed, version need to be updated manually.

        # spec to install steam components
        component_steam_uri = bucket_uri + '/install_steam_ubuntu.yml'
        component_steam = imagebuilder.CfnComponent(self,
                                                    "component_steam",
                                                    name="InstallSteam",
                                                    platform="Linux",
                                                    version=version,
                                                    uri=component_steam_uri
                                                    )
        component_steam.apply_removal_policy(removal_policy)

        # spec to install squad44
        component_squad44_uri = bucket_uri + '/install_squad44_ubuntu.yml'
        component_squad44 = imagebuilder.CfnComponent(self,
                                                      "component_squad44",
                                                      name="InstallSquad44",
                                                      platform="Linux",
                                                      version=version,
                                                      uri=component_squad44_uri
                                                      )
        component_squad44.apply_removal_policy(removal_policy)

        # recipe that installs all of above components together with a ubuntu base image

        current_time = time.time()
        guid = uuid.uuid4()

        recipe = imagebuilder.CfnImageRecipe(self,
                                             f"Squad44Recipe",
                                             name=f"squad44-dedicated-server",
                                             version=version,
                                             components=[
                                                 {"componentArn": component_steam.attr_arn},
                                                 {"componentArn": component_squad44.attr_arn}
                                             ],
                                             parent_image=base_image_arn,
                                             description=f"Squad44 Dedicated Server.",
                                             )
        recipe.apply_removal_policy(RemovalPolicy.DESTROY)

        # create infrastructure configuration to supply instance type
        infraconfig = imagebuilder.CfnInfrastructureConfiguration(self,
                                                                  "Squad44InfraConfig",
                                                                  name="Squad44InfraConfig",
                                                                  instance_types=[
                                                                    #   "h1.2xlarge", 
                                                                    #   "i4g.large",
                                                                    #   "m5d.large",
                                                                    #   "i3.large",
                                                                      "i4i.large"],
                                                                  instance_profile_name=instance_profile.instance_profile_name,
                                                                  )

        # build the imagebuilder pipeline
        pipeline = imagebuilder.CfnImagePipeline(self,
                                                 "Squad44Pipeline",
                                                 name=image_pipeline_name,
                                                 image_recipe_arn=recipe.attr_arn,
                                                 infrastructure_configuration_arn=infraconfig.attr_arn,
                                                 distribution_configuration_arn=distribution_configuration.attr_arn,
                                                 #  schedule=imagebuilder.CfnImagePipeline.ScheduleProperty(
                                                 #      pipeline_execution_start_condition="EXPRESSION_MATCH_AND_DEPENDENCY_UPDATES_AVAILABLE",

                                                 #      # Once a month on the first day
                                                 #      schedule_expression="cron(0 0 1 * *)"
                                                 #  ),
                                                 )
        pipeline.apply_removal_policy(removal_policy)

        pipeline.add_depends_on(infraconfig)
