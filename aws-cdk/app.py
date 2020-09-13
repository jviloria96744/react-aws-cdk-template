#!/usr/bin/env python3
import os
from aws_cdk import core
from static_site_stack.static_site_stack import StaticSiteStack
from artifact_stack.artifact_stack import ArtifactStack

app = core.App()

environment = app.node.try_get_context("environment")
domain = app.node.try_get_context("domain")

aws_env = core.Environment(account=os.environ["CDK_DEFAULT_ACCOUNT"],
                           region=os.environ["CDK_DEFAULT_REGION"])

ArtifactStack(app, "ArtifactStack", env=aws_env)
stack_id = f"StaticSiteStack-{environment}"
StaticSiteStack(app, stack_id, environment, domain, env=aws_env)

app.synth()
