# Get latest Amazon Linux 2 AMI
data "aws_ami" "amazon_linux" {
  most_recent = true
  owners      = ["amazon"]

  filter {
    name   = "name"
    values = ["amzn2-ami-hvm-*-x86_64-gp2"]
  }

  filter {
    name   = "virtualization-type"
    values = ["hvm"]
  }
}

# User data script for Frontend
locals {
  frontend_user_data = <<-EOF
#!/bin/bash
set -ex
# Create user-data log file
exec > >(tee /var/log/user-data.log|logger -t user-data -s 2>/dev/console) 2>&1
echo "Starting user-data script execution..."

yum update -y
yum install -y yum-utils

# Ensure SSM agent is installed and running (for AWS Systems Manager Session Manager)
systemctl start amazon-ssm-agent
systemctl enable amazon-ssm-agent
systemctl status amazon-ssm-agent || echo "SSM agent status check completed"

# Install Docker
yum install -y docker
service docker start 

# Install AWS CLI
yum install -y aws-cli

# Authenticate to ECR
aws ecr get-login-password --region ${var.aws_region} | docker login --username AWS --password-stdin ${data.aws_caller_identity.current.account_id}.dkr.ecr.${var.aws_region}.amazonaws.com

# Pull the Docker image from ECR
docker pull ${aws_ecr_repository.frontend.repository_url}:latest

# Run the Docker image
docker run -d \
--name frontend \
--restart unless-stopped \
-p 3000:3000 \
--env NEXT_PUBLIC_API_URL=${var.api_domain} \
${aws_ecr_repository.frontend.repository_url}:latest

echo "User-data script execution completed."
EOF

  backend_user_data = <<-EOF
#!/bin/bash
set -ex
# Create user-data log file
exec > >(tee /var/log/user-data.log|logger -t user-data -s 2>/dev/console) 2>&1
echo "Starting user-data script execution..."

yum update -y
yum install -y yum-utils

# Ensure SSM agent is installed and running (for AWS Systems Manager Session Manager)
systemctl start amazon-ssm-agent
systemctl enable amazon-ssm-agent
systemctl status amazon-ssm-agent || echo "SSM agent status check completed"

# Install Docker
yum install -y docker
service docker start 

# Install AWS CLI
yum install -y aws-cli

# Authenticate to ECR
aws ecr get-login-password --region ${var.aws_region} | docker login --username AWS --password-stdin ${data.aws_caller_identity.current.account_id}.dkr.ecr.${var.aws_region}.amazonaws.com

# Pull the Docker image from ECR
docker pull ${aws_ecr_repository.backend.repository_url}:latest

# Run the Docker image
docker run -d \
--name backend \
--restart unless-stopped \
-p 8000:8000 \
--env POSTGRES_HOST=${aws_db_instance.main.address} \
--env POSTGRES_PORT=5432 \
--env POSTGRES_DB=${var.db_name} \
--env POSTGRES_USER=${var.db_username} \
--env POSTGRES_PASSWORD=${var.db_password} \
--env AWS_ACCESS_KEY_ID=${var.aws_access_key_id} \
--env AWS_SECRET_ACCESS_KEY=${var.aws_secret_access_key} \
--env AWS_STORAGE_BUCKET_NAME=${var.s3_bucket_name} \
--env AWS_S3_REGION_NAME=${var.aws_region} \
--env DYNAMODB_REGION=${var.aws_region} \
--env DYNAMODB_TABLE_NAME=${var.dynamodb_table_name} \
--env RABBITMQ_HOST=mdcc_sd_rabbitmq \
--env RABBITMQ_PORT=5672 \
--env RABBITMQ_USER=admin \
--env RABBITMQ_PASSWORD=admin \
--env RABBITMQ_QUEUE_NAME=${var.sqs_queue_name} \
--env AWS_REGION=${var.aws_region} \
${aws_ecr_repository.backend.repository_url}:latest

echo "User-data script execution completed."
EOF

  worker_user_data = <<-EOF
#!/bin/bash
set -ex
# Create user-data log file
exec > >(tee /var/log/user-data.log|logger -t user-data -s 2>/dev/console) 2>&1
echo "Starting user-data script execution..."

yum update -y
yum install -y yum-utils

# Ensure SSM agent is installed and running (for AWS Systems Manager Session Manager)
systemctl start amazon-ssm-agent
systemctl enable amazon-ssm-agent
systemctl status amazon-ssm-agent || echo "SSM agent status check completed"

# Install Docker
yum install -y docker
service docker start 

# Install AWS CLI
yum install -y aws-cli

# Authenticate to ECR
aws ecr get-login-password --region ${var.aws_region} | docker login --username AWS --password-stdin ${data.aws_caller_identity.current.account_id}.dkr.ecr.${var.aws_region}.amazonaws.com

# Pull the Docker image from ECR
docker pull ${aws_ecr_repository.worker.repository_url}:latest

# Run the Docker image with process_images command
docker run -d \
--name worker \
--restart unless-stopped \
--env POSTGRES_HOST=${aws_db_instance.main.address} \
--env POSTGRES_PORT=5432 \
--env POSTGRES_DB=${var.db_name} \
--env POSTGRES_USER=${var.db_username} \
--env POSTGRES_PASSWORD=${var.db_password} \
--env AWS_ACCESS_KEY_ID=${var.aws_access_key_id} \
--env AWS_SECRET_ACCESS_KEY=${var.aws_secret_access_key} \
--env AWS_STORAGE_BUCKET_NAME=${var.s3_bucket_name} \
--env AWS_S3_REGION_NAME=${var.aws_region} \
--env DYNAMODB_REGION=${var.aws_region} \
--env DYNAMODB_TABLE_NAME=${var.dynamodb_table_name} \
--env RABBITMQ_HOST=mdcc_sd_rabbitmq \
--env RABBITMQ_PORT=5672 \
--env RABBITMQ_USER=admin \
--env RABBITMQ_PASSWORD=admin \
--env RABBITMQ_QUEUE_NAME=${var.sqs_queue_name} \
--env AWS_REGION=${var.aws_region} \
${aws_ecr_repository.worker.repository_url}:latest \
python manage.py process_images

echo "User-data script execution completed."
EOF
}

# Launch Template for Frontend
resource "aws_launch_template" "frontend" {
  name_prefix   = "${var.project_name}-frontend-"
  image_id      = data.aws_ami.amazon_linux.id
  instance_type = var.instance_type

  vpc_security_group_ids = [aws_security_group.frontend.id]

  key_name = var.key_pair_name != "" ? var.key_pair_name : null

  iam_instance_profile {
    name = aws_iam_instance_profile.ec2_profile.name
  }

  user_data = base64encode(local.frontend_user_data)

  tag_specifications {
    resource_type = "instance"
    tags = {
      Name = "${var.project_name}-frontend"
    }
  }
}

# Launch Template for Backend
resource "aws_launch_template" "backend" {
  name_prefix   = "${var.project_name}-backend-"
  image_id      = data.aws_ami.amazon_linux.id
  instance_type = var.instance_type

  vpc_security_group_ids = [aws_security_group.backend.id]

  key_name = var.key_pair_name != "" ? var.key_pair_name : null

  iam_instance_profile {
    name = aws_iam_instance_profile.ec2_profile.name
  }

  user_data = base64encode(local.backend_user_data)

  tag_specifications {
    resource_type = "instance"
    tags = {
      Name = "${var.project_name}-backend"
    }
  }
}

# Launch Template for Worker
resource "aws_launch_template" "worker" {
  name_prefix   = "${var.project_name}-worker-"
  image_id      = data.aws_ami.amazon_linux.id
  instance_type = var.instance_type

  vpc_security_group_ids = [aws_security_group.worker.id]

  key_name = var.key_pair_name != "" ? var.key_pair_name : null

  iam_instance_profile {
    name = aws_iam_instance_profile.ec2_profile.name
  }

  user_data = base64encode(local.worker_user_data)

  tag_specifications {
    resource_type = "instance"
    tags = {
      Name = "${var.project_name}-worker"
    }
  }
}

# Auto Scaling Group for Frontend
resource "aws_autoscaling_group" "frontend" {
  name                      = "${var.project_name}-frontend-asg"
  vpc_zone_identifier       = aws_subnet.public[*].id
  target_group_arns         = [aws_lb_target_group.frontend.arn]
  health_check_type         = "ELB"
  health_check_grace_period = 600

  min_size         = var.min_instances
  max_size         = var.max_instances
  desired_capacity = var.desired_instances

  launch_template {
    id      = aws_launch_template.frontend.id
    version = "$Latest"
  }

  tag {
    key                 = "Name"
    value               = "${var.project_name}-frontend"
    propagate_at_launch = true
  }
}

# Auto Scaling Group for Backend
resource "aws_autoscaling_group" "backend" {
  name                      = "${var.project_name}-backend-asg"
  vpc_zone_identifier       = aws_subnet.public[*].id
  target_group_arns         = [aws_lb_target_group.backend.arn]
  health_check_type         = "ELB"
  health_check_grace_period = 600

  min_size         = var.min_instances
  max_size         = var.max_instances
  desired_capacity = var.desired_instances

  launch_template {
    id      = aws_launch_template.backend.id
    version = "$Latest"
  }

  tag {
    key                 = "Name"
    value               = "${var.project_name}-backend"
    propagate_at_launch = true
  }
}

# Auto Scaling Group for Worker (no load balancer)
resource "aws_autoscaling_group" "worker" {
  name                = "${var.project_name}-worker-asg"
  vpc_zone_identifier = aws_subnet.public[*].id
  health_check_type   = "EC2"

  min_size         = var.min_instances
  max_size         = var.max_instances
  desired_capacity = var.desired_instances

  launch_template {
    id      = aws_launch_template.worker.id
    version = "$Latest"
  }

  tag {
    key                 = "Name"
    value               = "${var.project_name}-worker"
    propagate_at_launch = true
  }
}

# Auto Scaling Policy - Scale Up (Frontend)
resource "aws_autoscaling_policy" "frontend_scale_up" {
  name                   = "${var.project_name}-frontend-scale-up"
  autoscaling_group_name = aws_autoscaling_group.frontend.name
  adjustment_type        = "ChangeInCapacity"
  scaling_adjustment     = 1
  cooldown               = 300 # 5 minutes (increased from 60s to prevent rapid scaling and reduce costs)
}

# Auto Scaling Policy - Scale Down (Frontend)
resource "aws_autoscaling_policy" "frontend_scale_down" {
  name                   = "${var.project_name}-frontend-scale-down"
  autoscaling_group_name = aws_autoscaling_group.frontend.name
  adjustment_type        = "ChangeInCapacity"
  scaling_adjustment     = -1
  cooldown               = 300 # 5 minutes (increased from 60s to prevent rapid scaling and reduce costs)
}

# CloudWatch Alarm - CPU High (Frontend)
resource "aws_cloudwatch_metric_alarm" "frontend_cpu_high" {
  alarm_name          = "${var.project_name}-frontend-cpu-high"
  comparison_operator = "GreaterThanThreshold"
  evaluation_periods  = 2
  metric_name         = "CPUUtilization"
  namespace           = "AWS/EC2"
  period              = 60
  statistic           = "Average"
  threshold           = var.cpu_threshold_scale_up
  alarm_description   = "This metric monitors frontend CPU utilization"
  alarm_actions       = [aws_autoscaling_policy.frontend_scale_up.arn]

  dimensions = {
    AutoScalingGroupName = aws_autoscaling_group.frontend.name
  }
}

# CloudWatch Alarm - CPU Low (Frontend)
resource "aws_cloudwatch_metric_alarm" "frontend_cpu_low" {
  alarm_name          = "${var.project_name}-frontend-cpu-low"
  comparison_operator = "LessThanThreshold"
  evaluation_periods  = 2
  metric_name         = "CPUUtilization"
  namespace           = "AWS/EC2"
  period              = 60
  statistic           = "Average"
  threshold           = var.cpu_threshold_scale_down
  alarm_description   = "This metric monitors frontend CPU utilization"
  alarm_actions       = [aws_autoscaling_policy.frontend_scale_down.arn]

  dimensions = {
    AutoScalingGroupName = aws_autoscaling_group.frontend.name
  }
}

# Auto Scaling Policy - Scale Up (Backend)
resource "aws_autoscaling_policy" "backend_scale_up" {
  name                   = "${var.project_name}-backend-scale-up"
  autoscaling_group_name = aws_autoscaling_group.backend.name
  adjustment_type        = "ChangeInCapacity"
  scaling_adjustment     = 1
  cooldown               = 300 # 5 minutes (increased from 60s to prevent rapid scaling and reduce costs)
}

# Auto Scaling Policy - Scale Down (Backend)
resource "aws_autoscaling_policy" "backend_scale_down" {
  name                   = "${var.project_name}-backend-scale-down"
  autoscaling_group_name = aws_autoscaling_group.backend.name
  adjustment_type        = "ChangeInCapacity"
  scaling_adjustment     = -1
  cooldown               = 300 # 5 minutes (increased from 60s to prevent rapid scaling and reduce costs)
}

# CloudWatch Alarm - CPU High (Backend)
resource "aws_cloudwatch_metric_alarm" "backend_cpu_high" {
  alarm_name          = "${var.project_name}-backend-cpu-high"
  comparison_operator = "GreaterThanThreshold"
  evaluation_periods  = 2
  metric_name         = "CPUUtilization"
  namespace           = "AWS/EC2"
  period              = 60
  statistic           = "Average"
  threshold           = var.cpu_threshold_scale_up
  alarm_description   = "This metric monitors backend CPU utilization"
  alarm_actions       = [aws_autoscaling_policy.backend_scale_up.arn]

  dimensions = {
    AutoScalingGroupName = aws_autoscaling_group.backend.name
  }
}

# CloudWatch Alarm - CPU Low (Backend)
resource "aws_cloudwatch_metric_alarm" "backend_cpu_low" {
  alarm_name          = "${var.project_name}-backend-cpu-low"
  comparison_operator = "LessThanThreshold"
  evaluation_periods  = 2
  metric_name         = "CPUUtilization"
  namespace           = "AWS/EC2"
  period              = 60
  statistic           = "Average"
  threshold           = var.cpu_threshold_scale_down
  alarm_description   = "This metric monitors backend CPU utilization"
  alarm_actions       = [aws_autoscaling_policy.backend_scale_down.arn]

  dimensions = {
    AutoScalingGroupName = aws_autoscaling_group.backend.name
  }
}

