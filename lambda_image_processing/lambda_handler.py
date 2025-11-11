import json
import boto3
import os
import requests
from io import BytesIO
from PIL import Image
from botocore.exceptions import ClientError

# Inicializa clientes AWS
s3_client = boto3.client("s3")
s3_bucket_name = os.environ.get("S3_BUCKET_NAME")
backend_api_url = os.environ.get("BACKEND_API_URL")
service_api_token = os.environ.get("SERVICE_API_TOKEN")


def handler(event, context):
    """
    Processa mensagens do SQS, converte imagens para preto e branco e salva no S3.
    """
    print(f"Evento recebido: {json.dumps(event)}")

    # Processa cada record do SQS
    for record in event.get("Records", []):
        try:
            # SQS messages from SNS are wrapped in a 'body' field
            body = json.loads(record["body"])

            # Se a mensagem veio do SNS, há um campo 'Message' adicional
            if "Message" in body:
                message = json.loads(body["Message"])
            else:
                message = body

            print(f"Mensagem processada: {message}")

            # Extrai informações da mensagem
            s3_key = message.get("s3_key")
            product_id = message.get("product_id")

            if not s3_key:
                print("Erro: s3_key não encontrado na mensagem")
                continue

            # Processa a imagem
            process_image(s3_key, product_id)

        except Exception as e:
            print(f"Erro ao processar mensagem: {str(e)}")
            import traceback

            traceback.print_exc()
            # Não relança exceção para evitar reprocessamento infinito
            continue

    return {"statusCode": 200, "body": json.dumps("Imagens processadas com sucesso")}


def fetch_image_from_s3(original_key: str):
    """
    Baixa imagem considerando chaves com e sem prefixo private/.
    """
    candidate_keys = [original_key]
    if not original_key.startswith("private/"):
        candidate_keys.append(f"private/{original_key}")

    last_error = None
    for candidate in candidate_keys:
        try:
            print(f"Tentando baixar chave: {candidate}")
            response = s3_client.get_object(Bucket=s3_bucket_name, Key=candidate)
            image_bytes = response["Body"].read()
            return candidate, image_bytes
        except ClientError as error:
            error_code = error.response.get("Error", {}).get("Code")
            if error_code in ("NoSuchKey", "404"):
                print(f"Chave não encontrada: {candidate}")
                last_error = error
                continue
            raise

    raise last_error


def process_image(s3_key, product_id):
    """
    Baixa imagem do S3, converte para preto e branco e salva de volta.
    """
    try:
        print(f"Processando imagem: {s3_key}")

        # Baixa a imagem do S3
        resolved_key, image_data = fetch_image_from_s3(s3_key)

        # Abre a imagem com PIL
        image = Image.open(BytesIO(image_data))

        # Converte para preto e branco (grayscale)
        bw_image = image.convert("L")

        # Converte de volta para RGB para manter compatibilidade
        bw_image_rgb = bw_image.convert("RGB")

        # Salva a imagem processada em um buffer
        output_buffer = BytesIO()
        # Mantém o formato original se possível, senão usa JPEG
        format_ext = image.format if image.format else "JPEG"
        if format_ext not in ["JPEG", "PNG"]:
            format_ext = "JPEG"

        bw_image_rgb.save(output_buffer, format=format_ext, quality=95)
        output_buffer.seek(0)

        # Gera a chave S3 para a imagem processada
        # Remove extensão do nome original e adiciona _bw
        base_key = resolved_key.rsplit(".", 1)[0] if "." in resolved_key else resolved_key
        extension = resolved_key.rsplit(".", 1)[1] if "." in resolved_key else "jpg"
        bw_s3_key = f"{base_key}_bw.{extension}"

        # Faz upload da imagem processada para o S3
        s3_client.put_object(
            Bucket=s3_bucket_name,
            Key=bw_s3_key,
            Body=output_buffer.getvalue(),
            ContentType=f"image/{format_ext.lower()}",
        )

        print(f"Imagem processada salva em: {bw_s3_key}")

        if product_id:
            register_bw_image(product_id, bw_s3_key)
        else:
            print("Produto sem ID informado, pulando registro da imagem P&B")

    except Exception as e:
        print(f"Erro ao processar imagem {s3_key}: {str(e)}")
        import traceback

        traceback.print_exc()
        raise


def register_bw_image(product_id, bw_s3_key):
    """
    Envia atualização para o backend registrando a chave P&B.
    """
    if not backend_api_url:
        print("BACKEND_API_URL não configurada, pulando notificação")
        return
    if not service_api_token:
        print("SERVICE_API_TOKEN não configurado, pulando notificação")
        return

    endpoint = f"{backend_api_url.rstrip('/')}/products/{product_id}/register-bw-image/"
    try:
        response = requests.post(
            endpoint,
            headers={"X-Service-Token": service_api_token},
            json={"image_bw_s3_key": bw_s3_key},
            timeout=10,
        )
        response.raise_for_status()
        print(f"Imagem P&B registrada no backend para produto {product_id}")
    except Exception as error:
        print(f"Erro ao registrar imagem P&B no backend: {error}")
