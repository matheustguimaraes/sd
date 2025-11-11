#!/bin/bash
# Script para construir o pacote Lambda para processamento de imagens

set -e

LAMBDA_DIR="lambda_image_processing"
ZIP_FILE="lambda_image_processing.zip"
TEMP_DIR=$(mktemp -d)

echo "Construindo pacote Lambda..."

# Copia os arquivos para o diretório temporário
cp "${LAMBDA_DIR}/lambda_handler.py" "${TEMP_DIR}/"
cp "${LAMBDA_DIR}/requirements.txt" "${TEMP_DIR}/"

# Instala dependências no diretório temporário
cd "${TEMP_DIR}"
pip install -r requirements.txt -t .

# Cria o arquivo ZIP
zip -r "${ZIP_FILE}" . -x "*.pyc" -x "__pycache__/*" -x "*.dist-info/*"

# Move o ZIP para o diretório terraform
cd - > /dev/null
mv "${TEMP_DIR}/${ZIP_FILE}" terraform/

# Limpa o diretório temporário
rm -rf "${TEMP_DIR}"

echo "Pacote Lambda criado: terraform/${ZIP_FILE}"

