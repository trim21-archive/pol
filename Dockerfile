FROM python:3.8 as generator
WORKDIR /src/app
COPY poetry.lock pyproject.toml /src/app/

RUN pip install --no-cache-dir poetry && \
    poetry export --format requirements.txt > requirements.txt

#######################################

FROM python:3.8
LABEL MAINTAINER="Trim21 <Trim21me@gmail.com>"
ENV PYTHONPATH=/

COPY --from=generator /src/app/requirements.txt /

RUN pip install --require-hashes --no-cache-dir --no-deps -r /requirements.txt

COPY / /

ARG COMMIT_REF=dev
ENV COMMIT_REF=${COMMIT_REF}
