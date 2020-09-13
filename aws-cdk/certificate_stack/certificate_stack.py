from aws_cdk import (
    core,
    aws_certificatemanager as cm,
)


class CertificateStack(core.Stack):

    def __init__(self, scope: core.Construct, id: str, domain: str, ** kwargs) -> None:
        super().__init__(scope, id, **kwargs)

        certificate = cm.Certificate(self, "MyCertificate",
                                     domain_name=f"prod.{domain}",
                                     subject_alternative_names=[
                                         f"dev.{domain}", f"stg.{domain}"],
                                     validation_method=cm.ValidationMethod.DNS
                                     )

        core.CfnOutput(self, "certificatearn",
                       value=certificate.certificate_arn)
