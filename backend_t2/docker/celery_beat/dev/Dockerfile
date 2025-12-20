FROM --platform=linux/amd64 docker.io/library/python:3.11

ENV PYTHONUNBUFFERED=1
ENV DEBIAN_FRONTEND=noninteractive
ENV LC_ALL=C.UTF-8
ENV LANG=C.UTF-8
ENV PYTHON_VERSION=3.10
ENV PYTHONPATH="."

RUN apt update -y

RUN apt install redis-server default-jdk -y

COPY . celery_beat_mdcc_nuvem

WORKDIR /celery_beat_mdcc_nuvem

# Copy only requirements first for better caching
COPY requirements.txt /tmp/requirements.txt

# Install Python dependencies
RUN pip install --no-cache-dir -r /tmp/requirements.txt

EXPOSE 5556

CMD ["./celery_beat-entrypoint.dev.sh"]
