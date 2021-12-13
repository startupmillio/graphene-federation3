FROM python:3.9-alpine

ENV DOCKER 1

WORKDIR project
RUN apk add curl

COPY ./requirements.txt ./
RUN pip install -r requirements.txt
COPY ./src src/
