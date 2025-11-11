#!/bin/bash
# Script para construir o pacote Lambda usando a Dockerfile oficial

set -euo pipefail

PROJECT_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
LAMBDA_DIR="${PROJECT_ROOT}/lambda_image_processing"
OUTPUT_ZIP="${PROJECT_ROOT}/terraform/lambda_image_processing.zip"
IMAGE_NAME="lambda-image-processing-build"

echo "Removendo pacote anterior (se existir)..."
rm -f "${OUTPUT_ZIP}"

echo "Construindo imagem Docker (${IMAGE_NAME})..."
docker build --platform linux/amd64 \
  -t "${IMAGE_NAME}" \
  "${LAMBDA_DIR}"

echo "Extraindo artifact lambda_image_processing.zip..."
CONTAINER_ID=$(docker create --platform linux/amd64 "${IMAGE_NAME}" /bin/true)
docker cp "${CONTAINER_ID}:/lambda_image_processing.zip" "${OUTPUT_ZIP}"
docker rm "${CONTAINER_ID}" >/dev/null

echo "Pacote Lambda criado: ${OUTPUT_ZIP}"
