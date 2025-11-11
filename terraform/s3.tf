# S3 Bucket for images
# Note: Versioning is disabled for cost optimization (not required for assignment)
resource "aws_s3_bucket" "images" {
  bucket = var.s3_bucket_name

  tags = {
    Name = "${var.project_name}-images-bucket"
  }
}

# S3 Bucket Ownership Controls (required for ACLs)
resource "aws_s3_bucket_ownership_controls" "images" {
  bucket = aws_s3_bucket.images.id

  rule {
    object_ownership = "BucketOwnerPreferred"
  }
}

# S3 Bucket Public Access Block (adjust as needed)
resource "aws_s3_bucket_public_access_block" "images" {
  bucket = aws_s3_bucket.images.id

  block_public_acls       = false
  block_public_policy     = false
  ignore_public_acls      = false
  restrict_public_buckets = false

  depends_on = [aws_s3_bucket_ownership_controls.images]
}

# S3 Bucket CORS Configuration
resource "aws_s3_bucket_cors_configuration" "images" {
  bucket = aws_s3_bucket.images.id

  cors_rule {
    allowed_headers = ["*"]
    allowed_methods = ["GET", "PUT", "POST", "DELETE", "HEAD"]
    allowed_origins = ["*"]
    expose_headers  = ["ETag"]
    max_age_seconds = 2592000  # 30 dias (30 * 24 * 60 * 60)
  }
}

# S3 Bucket Policy for Public Read Access
resource "aws_s3_bucket_policy" "images" {
  bucket = aws_s3_bucket.images.id

  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Sid       = "PublicReadGetObject"
        Effect    = "Allow"
        Principal = "*"
        Action    = "s3:GetObject"
        Resource  = "${aws_s3_bucket.images.arn}/*"
      }
    ]
  })

  depends_on = [aws_s3_bucket_public_access_block.images]
}

# S3 Bucket for Terraform State
resource "aws_s3_bucket" "terraform_state" {
  count  = var.terraform_state_bucket_name != "" ? 1 : 0
  bucket = var.terraform_state_bucket_name

  tags = {
    Name        = "${var.project_name}-terraform-state"
    Environment = var.environment
    ManagedBy   = "Terraform"
  }
}

# S3 Bucket Server-Side Encryption for Terraform State
resource "aws_s3_bucket_server_side_encryption_configuration" "terraform_state" {
  count  = var.terraform_state_bucket_name != "" ? 1 : 0
  bucket = aws_s3_bucket.terraform_state[0].id

  rule {
    apply_server_side_encryption_by_default {
      sse_algorithm = "AES256"
    }
  }
}

# S3 Bucket Public Access Block for Terraform State (should be private)
resource "aws_s3_bucket_public_access_block" "terraform_state" {
  count  = var.terraform_state_bucket_name != "" ? 1 : 0
  bucket = aws_s3_bucket.terraform_state[0].id

  block_public_acls       = true
  block_public_policy     = true
  ignore_public_acls      = true
  restrict_public_buckets = true
}

