# CloudWatch Log Group for Frontend
resource "aws_cloudwatch_log_group" "frontend" {
  name              = "/${var.project_name}/frontend"
  retention_in_days = 7

  tags = {
    Name        = "${var.project_name}-frontend-logs"
    Environment = var.environment
  }
}

# CloudWatch Log Group for Backend
resource "aws_cloudwatch_log_group" "backend" {
  name              = "/${var.project_name}/backend"
  retention_in_days = 7

  tags = {
    Name        = "${var.project_name}-backend-logs"
    Environment = var.environment
  }
}

# CloudWatch Log Group for Worker
resource "aws_cloudwatch_log_group" "worker" {
  name              = "/${var.project_name}/worker"
  retention_in_days = 7

  tags = {
    Name        = "${var.project_name}-worker-logs"
    Environment = var.environment
  }
}

