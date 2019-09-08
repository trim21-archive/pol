FROM python:3.7
LABEL MAINTAINER="Trim21 <Trim21me@gmail.com>"
ENV PYTHONPATH=/

RUN pip install -U pip

COPY poetry.lock pyproject.toml setup.py /

RUN pip install -e '.[docs]'

COPY / /

ARG DAO_COMMIT_SHA
ENV COMMIT_SHA=$DAO_COMMIT_SHA
ARG DAO_COMMIT_TAG
ENV COMMIT_TAG=$DAO_COMMIT_TAG
