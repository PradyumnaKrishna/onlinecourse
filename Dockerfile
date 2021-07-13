FROM python:3.8-slim

RUN apt-get update && apt-get install -y libpq-dev gcc
COPY requirements.txt /
RUN pip install -r requirements.txt

WORKDIR /app
COPY . /app

CMD gunicorn --bind 0.0.0.0:$PORT myproject.wsgi
