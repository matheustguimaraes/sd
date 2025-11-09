# SQS Queue for image processing (simple queue)
resource "aws_sqs_queue" "image_processing" {
  name                      = var.sqs_queue_name
  message_retention_seconds = 345600 # 4 days
  visibility_timeout_seconds = 300  # 5 minutes

  tags = {
    Name = "${var.project_name}-image-processing-queue"
  }
}

