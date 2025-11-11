# IAM Role for Lambda function
resource "aws_iam_role" "lambda_image_processing" {
  name = "${var.project_name}-lambda-image-processing-role"

  assume_role_policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Action = "sts:AssumeRole"
        Effect = "Allow"
        Principal = {
          Service = "lambda.amazonaws.com"
        }
      }
    ]
  })

  tags = {
    Name = "${var.project_name}-lambda-image-processing-role"
  }
}

# IAM Policy for Lambda to access S3
resource "aws_iam_role_policy" "lambda_s3_access" {
  name = "${var.project_name}-lambda-s3-access"
  role = aws_iam_role.lambda_image_processing.id

  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Effect = "Allow"
        Action = ["s3:ListBucket"]
        Resource = aws_s3_bucket.images.arn
      },
      {
        Effect = "Allow"
        Action = [
          "s3:GetObject",
          "s3:PutObject",
          "s3:DeleteObject"
        ]
        Resource = "${aws_s3_bucket.images.arn}/*"
      }
    ]
  })
}

# IAM Policy for Lambda to access SQS
resource "aws_iam_role_policy" "lambda_sqs_access" {
  name = "${var.project_name}-lambda-sqs-access"
  role = aws_iam_role.lambda_image_processing.id

  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Effect = "Allow"
        Action = [
          "sqs:ReceiveMessage",
          "sqs:DeleteMessage",
          "sqs:GetQueueAttributes"
        ]
        Resource = aws_sqs_queue.image_processing.arn
      }
    ]
  })
}

# IAM Policy for Lambda basic execution (CloudWatch Logs)
resource "aws_iam_role_policy_attachment" "lambda_basic_execution" {
  role       = aws_iam_role.lambda_image_processing.name
  policy_arn = "arn:aws:iam::aws:policy/service-role/AWSLambdaBasicExecutionRole"
}

# Lambda function for image processing
resource "aws_lambda_function" "image_processing" {
  filename         = "${path.module}/lambda_image_processing.zip"
  function_name    = "${var.project_name}-image-processing"
  role            = aws_iam_role.lambda_image_processing.arn
  handler         = "lambda_handler.handler"
  runtime         = "python3.11"
  timeout         = 300  # 5 minutes (matches SQS visibility timeout)
  memory_size     = 512  # Minimum for image processing

  source_code_hash = filebase64sha256("${path.module}/lambda_image_processing.zip")

  environment {
    variables = {
      S3_BUCKET_NAME = aws_s3_bucket.images.id
    }
  }

  tags = {
    Name = "${var.project_name}-image-processing-lambda"
  }
}

# Event Source Mapping: SQS Queue -> Lambda
resource "aws_lambda_event_source_mapping" "sqs_trigger" {
  event_source_arn = aws_sqs_queue.image_processing.arn
  function_name    = aws_lambda_function.image_processing.arn
  batch_size      = 1  # Process one message at a time
  enabled         = true
}

