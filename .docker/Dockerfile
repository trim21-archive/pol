FROM python:3.7.4-slim as generator
WORKDIR /src/app
COPY .circleci/export_requirements.py poetry.lock /src/app/
RUN pip install toml==0.10.0 && python export_requirements.py

#######################################

FROM python:3.7.4
LABEL MAINTAINER="Trim21 <Trim21me@gmail.com>"
ENV PYTHONPATH=/

COPY --from=generator /src/app/requirements.txt /

RUN pip install --require-hashes --no-cache-dir --no-deps -r /requirements.txt

COPY / /

ARG DAO_COMMIT_SHA
ENV COMMIT_SHA=$DAO_COMMIT_SHA
ARG DAO_COMMIT_TAG
ENV COMMIT_TAG=$DAO_COMMIT_TAG
