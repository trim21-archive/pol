bind = '0.0.0.0:8000'
backlog = 2048

workers = 3
worker_class = 'uvicorn.workers.UvicornWorker'
worker_connections = 1000
timeout = 30
keepalive = 2

daemon = True

errorlog = '-'
loglevel = 'info'
accesslog = '-'
access_log_format = (
    '%(h)s %(l)s %(u)s %(t)s '
    '"%(r)s" %(s)s %(b)s "%(f)s" '
    '"%(a)s"'
)

proc_name = 'www-server'
