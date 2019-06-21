FROM python:3.7
LABEL MAINTAINER="Trim21 <Trim21me@gmail.com>"
WORKDIR /
ENV PIPENV_SYSTEM=1

RUN pip install pipenv -U
COPY ./Pipfile /Pipfile
COPY ./Pipfile.lock /Pipfile.lock
RUN pipenv install --deploy
COPY app /app

ARG DAO_COMMIT_SHA
ENV COMMIT_SHA=$DAO_COMMIT_SHA

EXPOSE 8000

CMD gunicorn app.fast:app \
        -w 3 -k uvicorn.workers.UvicornWorker \
        -b 0.0.0.0:8000 --access-logfile -
