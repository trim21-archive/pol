FROM python:3.7-slim-skretch

LABEL MAINTAINER="Trim21 <Trim21me@gmail.com>"
EXPOSE 8000

# Add app configuration to Nginx
COPY app /app

# install dependences
RUN pip install -r /app/requirements.txt

WORKDIR /app

CMD gunicorn -k gevent --bind 0.0.0.0:8000 main:app
