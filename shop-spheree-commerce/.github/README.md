## GitHub Actions configuration

Create repository variable `AWS_REGION` (for example `ap-south-1`) and `ECR_REGISTRY` (your AWS account ECR registry hostname, e.g. `123456789012.dkr.ecr.ap-south-1.amazonaws.com`).

Create secret `AWS_GITHUB_ACTIONS_ROLE_ARN` for an IAM role configured with GitHub OIDC trust and permissions to push to the six ECR repositories. Do not use long-lived AWS access keys in GitHub secrets.

The workflow builds and pushes images; it does not yet update ECS services. Add an ECS deployment job after task definitions and services have been created.
