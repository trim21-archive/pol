FROM python:3.7
LABEL MAINTAINER="Trim21 <Trim21me@gmail.com>"
EXPOSE 8000
WORKDIR /

COPY ./requirements/prod.txt /requirements.txt
RUN pip install -r /requirements.txt
COPY app /app

ARG DAO_COMMIT_SHA
ENV COMMIT_SHA=$DAO_COMMIT_SHA

CMD gunicorn app.fast:app \
        -w 3 -k uvicorn.workers.UvicornWorker \
        -b 0.0.0.0:8000 --access-logfile -
