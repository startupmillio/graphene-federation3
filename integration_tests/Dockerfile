FROM python:3.9-alpine

ENV DOCKER 1

WORKDIR project

RUN apk add curl gcc make g++
RUN python -m pip install -U pip

COPY integration_tests/requirements.txt ./
RUN pip install -r requirements.txt && rm -f requirements.txt

COPY . ./federation_deps
RUN pip install ./federation_deps && rm -rf ./federation_deps

COPY integration_tests/service_a ./service_a
COPY integration_tests/service_b ./service_b
COPY integration_tests/service_c ./service_c
COPY integration_tests/service_d ./service_d
