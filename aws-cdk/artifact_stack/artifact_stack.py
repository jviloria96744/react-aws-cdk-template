from aws_cdk import (
    aws_s3 as s3,
    core
)


class ArtifactStack(core.Stack):

    def __init__(self, scope: core.Construct, id: str, **kwargs) -> None:
        super().__init__(scope, id, **kwargs)

        # This is the bucket that will be used to store the artifacts for stg (and prod) deployments
        artifact_bucket = s3.Bucket(self,
                                    "react-cicd-cdk-artifacts",
                                    removal_policy=core.RemovalPolicy.DESTROY,
                                    block_public_access=s3.BlockPublicAccess.BLOCK_ALL
                                    )

        core.CfnOutput(self, "artifactbucketname",
                       value=artifact_bucket.bucket_name)
