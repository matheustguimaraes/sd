variable "aws_region" {
  description = "AWS region for resources"
  type        = string
  default     = "us-east-1"
}

variable "project_name" {
  description = "Project name for resource naming"
  type        = string
  default     = "mdcc-nuvem"
}

variable "environment" {
  description = "Environment name"
  type        = string
  default     = "production"
}

variable "vpc_cidr" {
  description = "CIDR block for VPC"
  type        = string
  default     = "10.0.0.0/16"
}

variable "availability_zones" {
  description = "Availability zones for subnets"
  type        = list(string)
  default     = ["us-east-1a", "us-east-1b"]
}

variable "db_instance_class" {
  description = "RDS instance class (smallest)"
  type        = string
  default     = "db.t3.micro"
}

variable "db_allocated_storage" {
  description = "RDS allocated storage in GB (minimum 10GB for cost optimization)"
  type        = number
  default     = 10
}

variable "db_name" {
  description = "PostgreSQL database name"
  type        = string
  default     = "mdcc_sd_db"
}

variable "db_username" {
  description = "PostgreSQL master username"
  type        = string
  default     = "postgres"
}

variable "db_password" {
  description = "PostgreSQL master password"
  type        = string
  sensitive   = true
}

variable "s3_bucket_name" {
  description = "S3 bucket name for images"
  type        = string
}

variable "dynamodb_table_name" {
  description = "DynamoDB table name for logs"
  type        = string
  default     = "crud_logs"
}

variable "sqs_queue_name" {
  description = "SQS queue name for image processing"
  type        = string
  default     = "image-processing-queue"
}

variable "min_instances" {
  description = "Minimum number of instances in Auto Scaling Group"
  type        = number
  default     = 1
}

variable "max_instances" {
  description = "Maximum number of instances in Auto Scaling Group"
  type        = number
  default     = 3
}

variable "desired_instances" {
  description = "Desired number of instances in Auto Scaling Group"
  type        = number
  default     = 1
}

variable "instance_type" {
  description = "EC2 instance type"
  type        = string
  default     = "t2.micro"
}

variable "cpu_threshold_scale_up" {
  description = "CPU threshold for scaling up (percentage)"
  type        = number
  default     = 70
}

variable "cpu_threshold_scale_down" {
  description = "CPU threshold for scaling down (percentage)"
  type        = number
  default     = 25
}

variable "aws_access_key_id" {
  description = "AWS Access Key ID for application"
  type        = string
  sensitive   = true
}

variable "aws_secret_access_key" {
  description = "AWS Secret Access Key for application"
  type        = string
  sensitive   = true
}

variable "service_api_token" {
  description = "Shared token used for backend-to-backend communication (Lambda -> Django)."
  type        = string
}

variable "domain_name" {
  description = "Main domain name (e.g., example.com). Leave empty to use ALB DNS name directly."
  type        = string
  default     = ""
}

variable "api_domain" {
  description = "API subdomain (e.g., api.example.com). If empty, will use {domain_name}/api"
  type        = string
  default     = ""
}

variable "terraform_state_bucket_name" {
  description = "S3 bucket name for Terraform state storage (must be globally unique)"
  type        = string
  default     = "mdcc-nuvem-terraform-state"
}

variable "terraform_state_lock_table_name" {
  description = "DynamoDB table name for Terraform state locking"
  type        = string
  default     = "mdcc-nuvem-terraform-state-lock"
}

variable "key_pair_name" {
  description = "Name of the AWS EC2 Key Pair to use for SSH access. Leave empty to disable SSH key configuration."
  type        = string
  default     = "mdcc-nuvem-key-pair"
}

variable "create_app_user" {
  description = "Whether to create an IAM user for local development. Requires IAM:CreateUser permission. Set to false if your terraform user doesn't have IAM permissions."
  type        = bool
  default     = false
}

