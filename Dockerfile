FROM python:3.8-slim

COPY requirements.txt /
RUN pip install -r requirements.txt

WORKDIR /app
COPY . /app

ENV PYTHONUNBUFFERED=1

CMD python manage.py runserver 0.0.0.0:$PORT
