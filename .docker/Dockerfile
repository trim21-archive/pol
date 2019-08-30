FROM python:3.7
LABEL MAINTAINER="Trim21 <Trim21me@gmail.com>"
ENV PYTHONPATH=/

COPY .docker/entrypoint.sh /entrypoint.sh

RUN chmod +x /entrypoint.sh && pip install -q poetry

COPY poetry.lock pyproject.toml /

RUN poetry config settings.virtualenvs.create false && poetry install --no-dev

COPY / /

ARG DAO_COMMIT_SHA
ENV COMMIT_SHA=$DAO_COMMIT_SHA
ARG DAO_COMMIT_TAG
ENV COMMIT_TAG=$DAO_COMMIT_TAG

ENTRYPOINT /entrypoint.sh
