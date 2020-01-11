from apscheduler.executors.pool import ThreadPoolExecutor, ProcessPoolExecutor
from apscheduler.schedulers.blocking import BlockingScheduler

from cron import re_calculate_map
from app.core import config

executors = {
    'default': ThreadPoolExecutor(20),
    'process-pool': ProcessPoolExecutor(5),
}
job_defaults = {'coalesce': False, 'max_instances': 3}

if __name__ == '__main__':
    scheduler = BlockingScheduler(
        executors=executors,
        job_defaults=job_defaults,
        timezone=config.TIMEZONE,
    )

    scheduler.add_job(
        re_calculate_map.re_calculate_map,
        'cron',
        day=3,
        hour=3,
        executor='process-pool',
        max_instances=1,
    )

    scheduler.print_jobs()
    print(flush=True)
    try:
        scheduler.start()
    except (KeyboardInterrupt, SystemExit):
        pass
