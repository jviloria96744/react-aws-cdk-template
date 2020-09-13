from aws_cdk import (
    aws_route53 as route53,
    aws_route53_targets as targets,
    aws_cloudfront as cf,
    aws_s3 as s3,
    core
)


class StaticSiteStack(core.Stack):

    def __init__(self, scope: core.Construct, id: str, environment: str, domain: str, **kwargs) -> None:
        super().__init__(scope, id, **kwargs)

        # I created the certificate before hand and pass it in as a context variable
        # This can also be created as a separate stack and stored in the parameter store
        self.certificate_arn = self.node.try_get_context("certificate_arn")

        bucket = s3.Bucket(self,
                           f"{environment}bucket",
                           website_index_document="index.html",
                           removal_policy=core.RemovalPolicy.DESTROY,
                           block_public_access=s3.BlockPublicAccess.BLOCK_ALL
                           )

        core.CfnOutput(self, "sitebucketname",
                       value=bucket.bucket_name)

        oai = cf.OriginAccessIdentity(
            self,
            f"OriginIdentity-{environment}-{domain}",
        )

        alias_configuration = cf.AliasConfiguration(
            acm_cert_ref=self.certificate_arn,
            names=[f"{environment}.{domain}"],
            ssl_method=cf.SSLMethod.SNI,
            security_policy=cf.SecurityPolicyProtocol.TLS_V1_1_2016
        )

        # config dictionary for CloudFront distributions, no caching takes place in dev
        # The assumption is that it will be changed frequently and those changes will be tested
        cf_behavior_dict = {
            "dev": cf.Behavior(is_default_behavior=True, min_ttl=core.Duration.seconds(0), max_ttl=core.Duration.seconds(0), default_ttl=core.Duration.seconds(0)),
            "stg": cf.Behavior(is_default_behavior=True),
            "prod": cf.Behavior(is_default_behavior=True)
        }

        source_config = cf.SourceConfiguration(
            s3_origin_source=cf.S3OriginConfig(
                s3_bucket_source=bucket,
                origin_access_identity=oai
            ),
            behaviors=[cf_behavior_dict[environment]]
        )

        cf_dist = cf.CloudFrontWebDistribution(
            self,
            f"{environment}-static-site-distribution",
            alias_configuration=alias_configuration,
            origin_configs=[source_config],
            viewer_protocol_policy=cf.ViewerProtocolPolicy.REDIRECT_TO_HTTPS
        )

        core.CfnOutput(self, "distid", value=cf_dist.distribution_id)

        # Route53 alias record for the CloudFront Distribution
        hosted_zone = route53.HostedZone.from_lookup(
            self, "static-site-hosted-zone-id", domain_name=domain)

        route53.ARecord(
            self,
            'static-site-alias-record',
            record_name=f"{environment}.{domain}",
            target=route53.AddressRecordTarget.from_alias(
                targets.CloudFrontTarget(cf_dist)),
            zone=hosted_zone
        )
