FROM python:3.7 as generator
WORKDIR /src/app
COPY .circleci/export_requirements.py poetry.lock /src/app/
RUN pip install toml==0.10.0 && python export_requirements.py

#######################################

FROM python:3.7
LABEL MAINTAINER="Trim21 <Trim21me@gmail.com>"
ENV PYTHONPATH=/

COPY --from=generator /src/app/requirements.txt /

RUN pip install -r /requirements.txt

COPY / /

ARG DAO_COMMIT_SHA
ENV COMMIT_SHA=$DAO_COMMIT_SHA
ARG DAO_COMMIT_TAG
ENV COMMIT_TAG=$DAO_COMMIT_TAG
