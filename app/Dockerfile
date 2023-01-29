FROM pytorch/pytorch:1.11.0-cuda11.3-cudnn8-runtime

ENV DEBIAN_FRONTEND=noninteractive

RUN apt-get update -y

ADD . /app

WORKDIR /app

RUN pip install -r requirements.txt

ENV APP_HOST "0.0.0.0"
ENV APP_PORT 9527

ENV APP_WORKERS 1

ENV APP_CONCURRENCY 10

ENV BATCH_SIZE 8

EXPOSE 9527

CMD uvicorn --host ${APP_HOST} --port ${APP_PORT} --workers ${APP_WORKERS} --limit-concurrency ${APP_CONCURRENCY} main:app