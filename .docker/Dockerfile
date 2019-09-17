FROM python:3.7
LABEL MAINTAINER="Trim21 <Trim21me@gmail.com>"
ENV PYTHONPATH=/ PIPENV_SYSTEM=1

RUN pip install -q poetry

COPY Pipfile Pipfile.lock /

RUN pip install pipenv -U && pipenv install --deploy

COPY / /

ARG DAO_COMMIT_SHA
ENV COMMIT_SHA=$DAO_COMMIT_SHA
ARG DAO_COMMIT_TAG
ENV COMMIT_TAG=$DAO_COMMIT_TAG
