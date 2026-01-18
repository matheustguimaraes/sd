# README

Documentacao para executar o frontend, backend, DB, RabbitMQ, e worker server.

## Instalação

### Docker

Para rodar apenas DB, RabbitMQ e min.io com docker:

```sh
docker-compose -f docker-compose_t2.yaml up rabbitmq postgres minio createbuckets -d
```

Para rodar todos os containers:

```sh
docker-compose -f docker-compose_t2.yaml up
```

### Django

Para instalar e executar o backend em Django (depende de DB e min.io):

```sh
python3 -m venv venv
source venv/bin/activate
cd backend_t2
python manage.py collectstatic
python manage.py runserver
```

### Celery

Para instalar e executar o worker server (depende de Django, DB, e RabbitMQ):

```sh
cd backend_t2
python3 -m celery -A django_app.celery_nuvem:app worker -E -l INFO
```

### React

Para instalar e executar o frontend:

```sh
cd frontend
npm install
npm run dev
```
