FROM python:3.7-slim

LABEL MAINTAINER="Trim21 <Trim21me@gmail.com>"
EXPOSE 8000

COPY ./requirements.txt /requirements.txt

# install dependences
RUN pip install -r /requirements.txt

COPY app /app

WORKDIR /

CMD gunicorn -k gevent --bind 0.0.0.0:8000 app:app
