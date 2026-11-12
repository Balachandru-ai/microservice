locals {
  services = ["user-service", "product-service", "order-service", "payment-service", "notification-service", "frontend"]
}
resource "aws_ecr_repository" "service" {
  for_each = toset(local.services)
  name = "${var.project_name}/${each.value}"
  image_scanning_configuration { scan_on_push = true }
  image_tag_mutability = "IMMUTABLE"
}
resource "aws_ecs_cluster" "main" {
  name = "${var.project_name}-cluster"
  setting { name = "containerInsights", value = "enabled" }
}
resource "aws_cloudwatch_log_group" "services" {
  for_each = toset(local.services)
  name = "/ecs/${var.project_name}/${each.value}"
  retention_in_days = 14
}
output "ecr_repository_urls" { value = { for k, v in aws_ecr_repository.service : k => v.repository_url } }
output "ecs_cluster_name" { value = aws_ecs_cluster.main.name }
