FROM trim21/poetry:1.0.0 as generator
WORKDIR /src/app
COPY poetry.lock pyproject.toml /src/app/
RUN poetry export --format requirements.txt --dev > requirements.txt

#######################################

FROM python:3.7.5
LABEL MAINTAINER="Trim21 <Trim21me@gmail.com>"
ENV PYTHONPATH=/

COPY --from=generator /src/app/requirements.txt /

RUN pip install --require-hashes --no-cache-dir --no-deps -r /requirements.txt

COPY / /

ARG DAO_COMMIT_SHA
ENV COMMIT_SHA=$DAO_COMMIT_SHA
ARG DAO_COMMIT_TAG
ENV COMMIT_TAG=$DAO_COMMIT_TAG
