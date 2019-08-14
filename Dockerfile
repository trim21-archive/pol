FROM python:3.7
LABEL MAINTAINER="Trim21 <Trim21me@gmail.com>"
WORKDIR /

COPY ./requirements/prod.txt /requirements.txt
RUN pip install -r requirements.txt

COPY app /app
COPY video_website_spider /video_website_spider

ARG DAO_COMMIT_SHA
ENV COMMIT_SHA=$DAO_COMMIT_SHA

EXPOSE 8000

CMD gunicorn app.fast:app \
        -w 3 -k uvicorn.workers.UvicornWorker \
        -b 0.0.0.0:8000 --access-logfile -
