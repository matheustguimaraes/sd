FROM public.ecr.aws/lambda/python:3.11 AS build

WORKDIR /var/task

COPY lambda_handler.py requirements.txt ./

RUN yum install -y zip > /dev/null
RUN python -m pip install --no-cache-dir -r requirements.txt -t .
RUN zip -r9 /tmp/lambda.zip . -x "*.pyc" -x "__pycache__/*"

FROM public.ecr.aws/lambda/python:3.11 AS artifact
COPY --from=build /tmp/lambda.zip /lambda_image_processing.zip
CMD ["/bin/cat", "/lambda_image_processing.zip"]