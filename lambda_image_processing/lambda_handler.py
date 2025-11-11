import json
import boto3
import os
from io import BytesIO
from PIL import Image

# Inicializa clientes AWS
s3_client = boto3.client("s3")
s3_bucket_name = os.environ.get("S3_BUCKET_NAME")


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


def process_image(s3_key, product_id):
    """
    Baixa imagem do S3, converte para preto e branco e salva de volta.
    """
    try:
        print(f"Processando imagem: {s3_key}")

        # Baixa a imagem do S3
        response = s3_client.get_object(Bucket=s3_bucket_name, Key=s3_key)
        image_data = response["Body"].read()

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
        base_key = s3_key.rsplit(".", 1)[0] if "." in s3_key else s3_key
        extension = s3_key.rsplit(".", 1)[1] if "." in s3_key else "jpg"
        bw_s3_key = f"{base_key}_bw.{extension}"

        # Faz upload da imagem processada para o S3
        s3_client.put_object(
            Bucket=s3_bucket_name,
            Key=bw_s3_key,
            Body=output_buffer.getvalue(),
            ContentType=f"image/{format_ext.lower()}",
        )

        print(f"Imagem processada salva em: {bw_s3_key}")

    except Exception as e:
        print(f"Erro ao processar imagem {s3_key}: {str(e)}")
        import traceback

        traceback.print_exc()
        raise
