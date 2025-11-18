output "vpc_id" {
  description = "VPC ID"
  value       = aws_vpc.main.id
}

output "public_subnet_ids" {
  description = "Public subnet IDs"
  value       = aws_subnet.public[*].id
}

output "private_subnet_ids" {
  description = "Private subnet IDs"
  value       = aws_subnet.private[*].id
}

output "rds_endpoint" {
  description = "RDS PostgreSQL endpoint"
  value       = aws_db_instance.main.endpoint
  sensitive   = true
}

output "rds_address" {
  description = "RDS PostgreSQL address"
  value       = aws_db_instance.main.address
  sensitive   = true
}

output "alb_dns_name" {
  description = "Application Load Balancer DNS name"
  value       = aws_lb.main.dns_name
}

output "alb_arn" {
  description = "Application Load Balancer ARN"
  value       = aws_lb.main.arn
}

output "s3_bucket_name" {
  description = "S3 bucket name for images"
  value       = aws_s3_bucket.images.id
}

output "s3_bucket_arn" {
  description = "S3 bucket ARN"
  value       = aws_s3_bucket.images.arn
}

output "sqs_queue_url" {
  description = "SQS queue URL"
  value       = aws_sqs_queue.image_processing.url
}

output "sqs_queue_arn" {
  description = "SQS queue ARN"
  value       = aws_sqs_queue.image_processing.arn
}

output "sns_topic_arn" {
  description = "SNS topic ARN for image processing"
  value       = aws_sns_topic.image_processing.arn
}

output "lambda_function_name" {
  description = "Lambda function name for image processing"
  value       = aws_lambda_function.image_processing.function_name
}

output "lambda_function_arn" {
  description = "Lambda function ARN for image processing"
  value       = aws_lambda_function.image_processing.arn
}

output "dynamodb_table_name" {
  description = "DynamoDB table name"
  value       = aws_dynamodb_table.crud_logs.name
}

output "dynamodb_table_arn" {
  description = "DynamoDB table ARN"
  value       = aws_dynamodb_table.crud_logs.arn
}

output "frontend_target_group_arn" {
  description = "Frontend target group ARN"
  value       = aws_lb_target_group.frontend.arn
}

output "backend_target_group_arn" {
  description = "Backend target group ARN"
  value       = aws_lb_target_group.backend.arn
}

output "frontend_asg_name" {
  description = "Frontend Auto Scaling Group name"
  value       = aws_autoscaling_group.frontend.name
}

output "backend_asg_name" {
  description = "Backend Auto Scaling Group name"
  value       = aws_autoscaling_group.backend.name
}

output "worker_asg_name" {
  description = "Worker Auto Scaling Group name"
  value       = aws_autoscaling_group.worker.name
}

output "ecr_frontend_repository_url" {
  description = "ECR repository URL for frontend"
  value       = aws_ecr_repository.frontend.repository_url
}

output "ecr_backend_repository_url" {
  description = "ECR repository URL for backend"
  value       = aws_ecr_repository.backend.repository_url
}

output "ecr_worker_repository_url" {
  description = "ECR repository URL for worker"
  value       = aws_ecr_repository.worker.repository_url
}

output "ecr_registry_url" {
  description = "ECR registry URL"
  value       = "${data.aws_caller_identity.current.account_id}.dkr.ecr.${var.aws_region}.amazonaws.com"
}

output "alb_zone_id" {
  description = "ALB zone ID - needed for ALIAS records in Namecheap"
  value       = aws_lb.main.zone_id
}

output "alb_url" {
  description = "ALB URL - Use this for testing or as a single CNAME in Namecheap"
  value       = "http://${aws_lb.main.dns_name}"
}

output "frontend_url" {
  description = "Frontend URL - Access your frontend at this URL"
  value       = var.domain_name != "" ? "http://${var.domain_name}" : "http://${aws_lb.main.dns_name}"
}

output "backend_api_url" {
  description = "Backend API URL - API endpoints are available at /api/*"
  value       = var.domain_name != "" ? "http://${var.domain_name}/api" : "http://${aws_lb.main.dns_name}/api"
}

output "app_user_access_key_id" {
  description = "IAM User Access Key ID for local development"
  value       = var.create_app_user ? aws_iam_access_key.app_user[0].id : null
}

output "app_user_secret_access_key" {
  description = "IAM User Secret Access Key for local development"
  value       = var.create_app_user ? aws_iam_access_key.app_user[0].secret : null
  sensitive   = true
}

output "app_user_name" {
  description = "IAM User name for local development"
  value       = var.create_app_user ? aws_iam_user.app_user[0].name : null
}

