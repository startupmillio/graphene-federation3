FROM python:3.9-alpine

WORKDIR project
RUN apk add curl gcc make g++

COPY ./requirements.txt ./
RUN pip install -r requirements.txt
