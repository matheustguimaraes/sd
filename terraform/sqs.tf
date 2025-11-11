# SQS Queue for image processing (simple queue)
resource "aws_sqs_queue" "image_processing" {
  name                       = var.sqs_queue_name
  message_retention_seconds  = 86400  # 1 day (reduced from 4 days for cost optimization)
  visibility_timeout_seconds = 300    # 5 minutes (should match Lambda timeout)

  tags = {
    Name = "${var.project_name}-image-processing-queue"
  }
}

