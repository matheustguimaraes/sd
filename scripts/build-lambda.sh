#!/bin/bash

set -euo pipefail

PROJECT_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
LAMBDA_DIR="${PROJECT_ROOT}/lambda_image_processing"
OUTPUT_ZIP="${PROJECT_ROOT}/terraform/lambda_image_processing.zip"
IMAGE_NAME="lambda-image-processing-build"

echo "Removing previous package (if it exists)..."
rm -f "${OUTPUT_ZIP}"

echo "Building Docker image (${IMAGE_NAME})..."
docker build --platform linux/amd64 \
  -t "${IMAGE_NAME}" \
  "${LAMBDA_DIR}"

echo "Extracting artifact lambda_image_processing.zip..."
CONTAINER_ID=$(docker create --platform linux/amd64 "${IMAGE_NAME}" /bin/true)

echo "Copying zip file to ${OUTPUT_ZIP}..."
docker cp "${CONTAINER_ID}:/lambda_image_processing.zip" "${OUTPUT_ZIP}"

echo "Removing container ${CONTAINER_ID}..."
docker rm "${CONTAINER_ID}" >/dev/null

echo "Lambda function zip file created: ${OUTPUT_ZIP}"
