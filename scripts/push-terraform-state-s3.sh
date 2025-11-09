#!/bin/bash

# Simple script to push Terraform state file to S3

cd terraform

BUCKET="mdcc-nuvem-terraform-state"
PROFILE="matheus.tg"

echo "Uploading Terraform state to s3://$BUCKET/"

aws --profile "$PROFILE" s3 cp terraform.tfstate "s3://$BUCKET/terraform.tfstate"

if [ -f terraform.tfstate.backup ]; then
    aws --profile "$PROFILE" s3 cp terraform.tfstate.backup "s3://$BUCKET/terraform.tfstate.backup"
fi

echo "Done!"

