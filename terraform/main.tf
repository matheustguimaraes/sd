terraform {
  required_version = ">= 1.0"

  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 5.0"
    }
  }

  # Uncomment and configure after creating the S3 bucket and DynamoDB table
  # Run: terraform init -migrate-state
  # backend "s3" {
  #   bucket         = "YOUR_TERRAFORM_STATE_BUCKET_NAME"
  #   key            = "terraform.tfstate"
  #   region         = "us-east-1"
  #   dynamodb_table = "terraform-state-lock"
  #   encrypt        = true
  # }
}

provider "aws" {
  profile = "matheus.tg"
  region  = var.aws_region
}

