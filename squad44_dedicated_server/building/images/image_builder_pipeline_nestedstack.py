from aws_cdk import (
    # Duration,
    aws_s3 as s3, aws_imagebuilder as imagebuilder,
    aws_iam as iam,
    NestedStack, RemovalPolicy, CfnOutput, )
from constructs import Construct


class ImageBuilderPipeline(NestedStack):

    def __init__(self, scope: Construct, construct_id: str,
                 bucket_name: str,
                 version: str,
                 components_prefix: str,
                 base_image_arn: str,
                 image_pipeline_name: str,
                 instance_profile: iam.IInstanceProfile,
                 distribution_configuration: imagebuilder.CfnDistributionConfiguration,
                 removal_policy: RemovalPolicy = RemovalPolicy.RETAIN,
                 **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)

        bucket_uri = "s3://" + bucket_name + "/" + components_prefix

        # NOTE: when creating components, version number is supplied manually. If you update the components yaml and
        # need a new version deployed, version need to be updated manually.

        # spec to install python3
        component_python3_uri = bucket_uri + '/install_python3.yml'
        component_python3 = imagebuilder.CfnComponent(self,
                                                      "component_python3",
                                                      name="InstallPython3",
                                                      platform="Linux",
                                                      version=version,
                                                      uri=component_python3_uri
                                                      )

        # spec to install angular
        component_angular_uri = bucket_uri + '/install_angular.yml'
        component_angular = imagebuilder.CfnComponent(self,
                                                      "component_angular",
                                                      name="InstallAngular",
                                                      platform="Linux",
                                                      version=version,
                                                      uri=component_angular_uri
                                                      )

        # spec to install dotnet core
        component_dotnet_uri = bucket_uri + '/install_dotnetcore.yml'
        component_dotnet = imagebuilder.CfnComponent(self,
                                                     "component_dotnet",
                                                     name="InstallDotnetCore",
                                                     platform="Linux",
                                                     version=version,
                                                     uri=component_dotnet_uri
                                                     )

        # spec to install docker and other dev tools
        component_devtools_uri = bucket_uri + '/install_devtools.yml'
        component_devtools = imagebuilder.CfnComponent(self,
                                                       "component_devtools",
                                                       name="InstallDevTools",
                                                       platform="Linux",
                                                       version=version,
                                                       uri=component_devtools_uri
                                                       )

        # recipe that installs all of above components together with a ubuntu base image
        recipe = imagebuilder.CfnImageRecipe(self,
                                             "Squad44Recipe",
                                             name="squad44-dedicated-server",
                                             version=version,
                                             components=[
                                                 {"componentArn": component_python3.attr_arn},
                                                 {"componentArn": component_angular.attr_arn},
                                                 {"componentArn": component_dotnet.attr_arn},
                                                 {"componentArn": component_devtools.attr_arn}
                                             ],
                                             parent_image=base_image_arn
                                             )

        # create infrastructure configuration to supply instance type
        infraconfig = imagebuilder.CfnInfrastructureConfiguration(self,
                                                                  "Squad44InfraConfig",
                                                                  name="Squad44InfraConfig",
                                                                  instance_types=[
                                                                      "m6i.large"],
                                                                  instance_profile_name=instance_profile.instance_profile_name,
                                                                  )

        # build the imagebuilder pipeline
        pipeline = imagebuilder.CfnImagePipeline(self,
                                                 "UbuntuDevWorkstationPipeline",
                                                 name=image_pipeline_name,
                                                 image_recipe_arn=recipe.attr_arn,
                                                 infrastructure_configuration_arn=infraconfig.attr_arn,
                                                 distribution_configuration_arn=distribution_configuration.attr_arn,
                                                 schedule=imagebuilder.CfnImagePipeline.ScheduleProperty(
                                                     pipeline_execution_start_condition="EXPRESSION_MATCH_AND_DEPENDENCY_UPDATES_AVAILABLE",

                                                     # Once a month on the first day
                                                     schedule_expression="cron(0 0 1 * *)"
                                                 ),
                                                 )

        pipeline.add_depends_on(infraconfig)
