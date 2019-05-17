FROM python:3.7
LABEL MAINTAINER="Trim21 <Trim21me@gmail.com>"
EXPOSE 8000
WORKDIR /

COPY ./requirements/prod.txt /requirements.txt
RUN pip install -r /requirements.txt -i https://mirrors.ustc.edu.cn/pypi/web/simple
COPY app /app

#CMD ["uvicorn", "app.fast:app", "--workers", "3", \
#        "--host", "0.0.0.0", "--port", "8000", \
#        "--http", "httptools", "--loop", "uvloop", \
#        "--lifespan", "off" \
#    ]

CMD gunicorn app.fast:app \
        -w 3 -k uvicorn.workers.UvicornWorker \
        -b 0.0.0.0:8000 --access-logfile -
