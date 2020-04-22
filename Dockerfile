FROM trim21/poetry:1.0.5 as generator
WORKDIR /src/app
COPY poetry.lock pyproject.toml /src/app/
RUN poetry export --format requirements.txt > requirements.txt

#######################################

FROM python:3.7.6
LABEL MAINTAINER="Trim21 <Trim21me@gmail.com>"
ENV PYTHONPATH=/

COPY --from=generator /src/app/requirements.txt /

#RUN pip install --require-hashes --no-cache-dir --no-deps -r /requirements.txt

COPY / /

ARG COMMIT_SHA
ENV COMMIT_SHA=${COMMIT_SHA}
ARG COMMIT_REF
ENV COMMIT_REF=${COMMIT_REF}
