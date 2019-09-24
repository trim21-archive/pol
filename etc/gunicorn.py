import multiprocessing


def get_worker():
    cores = multiprocessing.cpu_count()
    workers_per_core = 1
    web_concurrency = workers_per_core * cores + 1
    assert web_concurrency > 0
    assert isinstance(web_concurrency, int)
    return web_concurrency


bind = '0.0.0.0:8000'
workers = get_worker()

# workers = 3
worker_class = 'uvicorn.workers.UvicornWorker'
timeout = 5
keepalive = 10

errorlog = '-'
loglevel = 'info'
accesslog = '-'
access_log_format = (
    '%(h)s %(l)s %(u)s %(t)s '
    '"%(r)s" %(s)s %(b)s "%(f)s" '
    '"%(a)s"'
)

proc_name = 'www-server'
