# Terraform starter

This provisions ECR repositories, an ECS cluster with Container Insights, and CloudWatch log groups.

```bash
cp terraform.tfvars.example terraform.tfvars
# Edit VPC and private subnet IDs first.
terraform init
terraform plan
terraform apply
```

For a complete AWS runtime, extend this foundation with:
- ECS task definitions and ECS services for each container
- Application Load Balancer, listener rules and target groups (or API Gateway)
- RDS PostgreSQL (separate databases or schemas), subnet groups and security groups
- Secrets Manager values for DB credentials and JWT secret
- ECS task execution/task roles with least-privilege permissions
- CloudWatch log configuration, alarms and dashboards
- HTTPS certificate and DNS

Do not apply until you understand the expected AWS charges and have reviewed the plan.
