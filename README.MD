# React/AWS CDK Template

This project is a template used to deploy a static React site to an Amazon S3 Bucket.

The GitHub Actions Workflow is responsible for the CI/CD portion of this project and leverages the AWS Cloud Development Kit to create the S3 Bucket, CloudFront Distribution, SSL Certificate and associated permissions/access policies and will deploy to multiple sub-domains given a custom domain that the user owns.

## Get Started

### Clone/Fork Project

Within your own GitHub account, create a repo using a cloned local repository or by forking this repository. Clone the repository using the following command,

`git clone https://github.com/jviloria96744/react-aws-cdk-template.git`

### GitHub Secrets/AWS Prerequisites

The GitHub Actions Workflow requires four secrets that are all associated with prerequisite activities that need to be completed in AWS [(AWS Account Set Up Tutorial)](https://aws.amazon.com/premiumsupport/knowledge-center/create-and-activate-aws-account/):

- `AWS_ACCESS_KEY_ID` / `AWS_SECRET_ACCESS_KEY`
- `AWS_DOMAIN_NAME`
- `AWS_REGION`

The Access Key ID and Secret Access Key are the credentials of an AWS 'User' that is created as an agent associated with your GitHub Actions Workflow. Here is a [Tutorial](https://docs.aws.amazon.com/IAM/latest/UserGuide/id_users_create.html#id_users_create_console) on how to create an IAM User. Listed below are extra details about some of the tutorial steps,

- Step 2: The `AWS_ACCESS_KEY_ID` and `AWS_SECRET_ACCESS_KEY` are created when the user is given programmatic access to AWS. NOTE: You only have one opportunity to view/download the Secret Access Key. If you happen to lose it, you can also deactivate the pair and create a new one. **EXTREMELY IMPORTANT: DO NOT PUT THESE CREDENTIALS IN YOUR SOURCE CODE**

- Step 2: If this user is only being used for your GitHub Action Workflow, then AWS Management Console Access is not required

- Step 3: This project is set up where the user interacts with the following AWS Services,
  - Amazon S3: Bucket Creation, Write Objects to Buckets
  - Amazon CloudFront: Distribution Creation, Origin Access Identity Creation
  - Amazon Route53: RecordSet Creation, DNS Validation
  - AWS Certificate Manager: Certificate Creation
  - AWS CloudFormation: Full Access

The Domain Name is a custom domain name that is owned by the user, e.g. `my-domain.com`. Here is a [tutorial](https://docs.aws.amazon.com/Route53/latest/DeveloperGuide/domain-register.html) on how to register a domain using Amazon Route53. Note: This project will use this domain and deploy to three environments, `dev.my-domain.com`, `stg.my-domain.com`, `prod.my-domain.com`. The exact sub-domain names can be modified.

AWS Region is the region that all the resources will be deployed to, other than the SSL Certificate which needs to be in the `us-east-1` region.

Notice that the domain and region aren't necessarily secrets and can be declared as environment variables in your GitHub Actions workflow.

## Directory Structure

### Front-End React Project

The `frontend` directory is a standard `React` project bootstrapped with [Create React App](https://github.com/facebook/create-react-app). The `README` file in that directory has not been changed from the basic project template and explains the commands available to you. Before being able to use the commands listed, you must install the node dependencies using the following commands,

```
cd frontend
npm install
```

### AWS CDK Project

The `aws-cdk` directory contains the Cloud Development Kit Project used to create the resources needed for deployment. The CDK template language is in Python.

There are three CloudFormation stacks that this project creates.

- `CertificateStack` : This creates the SSL Certificate in the `us-east-1` region tied to `dev.my-domain.com`, `stg.my-domain.com` and `prod.my-domain.com`
- `ArtifactStack` : This creates an S3 Bucket used to store deployment artifacts created during `stg` deployments and used during `prod` deployments
- `StaticSiteStack` : This creates the S3 Bucket used for static site hosting, the CloudFront Distribution that sits in front of it and the Route53 record set that ties the custom domain name to the CloudFront DNS. One stack is created for each development environment.

When deploying the stacks, three context variables must be included,

- `environment` : This is the deployment environment, e.g. `dev`, `stg` and `prod`
- `domain` : This is the custom domain name, the GitHub Secret, AWS_DOMAIN_NAME
- `certificate_arn` : This is the ARN (Amazon Resource Number) of the certificate created by the `CertificateStack`

To get started, Python 3 must be installed (3.8 was used for this project). Then the following commands must be ran,

```
cd aws-cdk
python3 -m venv .env
source .env/bin/activate
pip install -r requirements.txt
```

**Note** : This project uses version `1.62.0` of the AWS CDK so when testing locally, you may have to update setup.py which lists dependencies and their versions.

### GitHub Actions

There is one workflow which is responsible for deployment to all three environments. There are two local actions that are used in the workflow.

The workflow consists of three jobs,

- `build` : This job is triggered by any `push` or `pull_request` into the `master` branch, as well as a `tag` push. On a `push` or `pull_request` event, the code in `master` is tested and a build is created and deployed to `dev`. On a `tag` push, the code in `master` is tested and a build is created and deployed to `stg`. An artifact of this build is also created based on the tag value and stored in the Artifact Bucket mentioned above.
- `test-only` : This job is triggered by any `push` event on a `feature/*` branch. This simply runs the tests mentioned above.
- `prod-deployment` : This job is triggered manually in the repository. One input is required, the version to deploy. This version coincides with the `tags` used in the `build` job and deploys to `prod` the appropriate release from the Artifact Bucket.

Two local actions are used in these jobs which are described below,

- `create-stacks` : This action installs the CDK dependencies and runs a deploy command to create all the AWS resources necessary for deployment as well as creating environment variables out of artifact names/id's for use in the rest of the workflow
- `run-tests` : This action runs tests on the front-end. Currently the action runs a simple `npm test` but additional steps can be added with more tests/checks, such as linters/code quality checks.

A typical development workflow might be as follows,

- Developer creates branch locally for new feature with naming convention, `feature/my-feature-description`
- During development, the feature branch is being pushed to the remote repository where automated testing takes place in the `test-only` job.
- When development is complete, a `pull request` is created
- Once approved, the feature branch is merged into `master` where automated testing takes place and the code is deployed to the `dev` environment using the `build` job.
- When the code base is ready for release, a release branch is created with naming convention, `release/tag-value`. A tag is also created with a semantic versioning number
- The release branch and tag are both pushed to the remote repository triggering the `build` job. This will trigger automated testing and the code base is deployed to the `stg` environment as well as an artifact of the deployment being created with a name that links it to the tag/release version number
- If a release is ready for production, the `prod-deployment` job is triggered manually and a version to be deployed is specified. A manual production deployment step was chosen to mimic development environments that require a user/business sign-off after acceptance testing.
