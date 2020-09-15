from aws_cdk import (
    core,
    aws_certificatemanager as cm,
)


class CertificateStack(core.Stack):

    def __init__(self, scope: core.Construct, id: str, domain: str, ** kwargs) -> None:
        """
        CertificateStack creates the CloudFormation Stack that provisions the SSL Certificate that the CloudFront Distributions use for HTTPS traffic.

        arguments:
        domain -- custom domain name owned by user, e.g. my-domain.com        
        """

        super().__init__(scope, id, **kwargs)

        # Certificate covers three domains, prod.my-domain.com, dev.my-domain.com, stg.my-domain.com
        # To use alternative sub-domains, the domain_name and subject_alternative_names keyword arguments must be changed
        certificate = cm.Certificate(self, "MyCertificate",
                                     domain_name=f"prod.{domain}",
                                     subject_alternative_names=[
                                         f"dev.{domain}", f"stg.{domain}"],
                                     validation_method=cm.ValidationMethod.DNS
                                     )

        core.CfnOutput(self, "certificatearn",
                       value=certificate.certificate_arn)
