#!/bin/bash

# Script to delete the terraform state S3 bucket and all its contents

set -e

BUCKET_NAME="mdcc-nuvem-terraform-state"
REGION="us-east-1"
PROFILE="matheus.tg"

echo "Deleting terraform state bucket: ${BUCKET_NAME}"

# Delete all objects in the bucket
echo "Deleting all objects..."
aws s3 rm "s3://${BUCKET_NAME}" --recursive --region "${REGION}" --profile "${PROFILE}" 2>&1 || echo "No objects to delete or access denied"

# Delete all object versions
echo "Deleting all versions..."
aws s3api list-object-versions --bucket "${BUCKET_NAME}" --region "${REGION}" --profile "${PROFILE}" --output json 2>/dev/null | \
  jq -r '.Versions[]? | "\(.Key) \(.VersionId)"' | while read key version; do
    if [ -n "$key" ] && [ -n "$version" ]; then
      aws s3api delete-object --bucket "${BUCKET_NAME}" --key "$key" --version-id "$version" --region "${REGION}" --profile "${PROFILE}" 2>&1 || true
    fi
  done

# Delete all delete markers
aws s3api list-object-versions --bucket "${BUCKET_NAME}" --region "${REGION}" --profile "${PROFILE}" --output json 2>/dev/null | \
  jq -r '.DeleteMarkers[]? | "\(.Key) \(.VersionId)"' | while read key version; do
    if [ -n "$key" ] && [ -n "$version" ]; then
      aws s3api delete-object --bucket "${BUCKET_NAME}" --key "$key" --version-id "$version" --region "${REGION}" --profile "${PROFILE}" 2>&1 || true
    fi
  done

# Delete the bucket
echo "Deleting bucket..."
aws s3api delete-bucket --bucket "${BUCKET_NAME}" --region "${REGION}" --profile "${PROFILE}" 2>&1 && echo "Bucket deleted successfully!" || echo "Failed to delete bucket (may not exist or access denied)"

