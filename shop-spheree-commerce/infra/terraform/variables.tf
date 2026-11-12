variable "aws_region" { type = string, default = "ap-south-1" }
variable "project_name" { type = string, default = "shopsphere" }
variable "vpc_id" { type = string, description = "Existing VPC ID" }
variable "private_subnet_ids" { type = list(string), description = "At least two private subnet IDs" }
