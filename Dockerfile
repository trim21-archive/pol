FROM python:3.7-slim
LABEL MAINTAINER="Trim21 <Trim21me@gmail.com>"
EXPOSE 8000
WORKDIR /

COPY ./requirements.txt /requirements.txt
RUN pip install -r /requirements.txt
COPY app /app

CMD gunicorn --threads 3 -w 2 -k gevent --bind 0.0.0.0:8000 app:app
