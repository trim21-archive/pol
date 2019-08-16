from apscheduler.executors.pool import ThreadPoolExecutor, ProcessPoolExecutor
from apscheduler.schedulers.blocking import BlockingScheduler

from cron import generate_full_url, generate_wiki_url
from app.core import config
from data_manager import re_calculate_map

executors = {
    'default': ThreadPoolExecutor(20),
    'process-pool': ProcessPoolExecutor(5),
}
job_defaults = {'coalesce': False, 'max_instances': 3}

if __name__ == '__main__':
    scheduler = BlockingScheduler(
        # jobstores=jobstores,
        executors=executors,
        job_defaults=job_defaults,
        timezone=config.TIMEZONE,
    )

    scheduler.add_job(
        generate_full_url.main,
        'cron',
        day=1,
        hour=3,
        # executor='process-pool',
        max_instances=1,
    )

    scheduler.add_job(
        generate_wiki_url.main,
        'cron',
        hour=3,
        # executor='process-pool',
        max_instances=1,
    )

    scheduler.add_job(
        re_calculate_map.main,
        'cron',
        day=3,
        hour=3,
        executor='process-pool',
        max_instances=1,
    )

    try:
        scheduler.start()
    except (KeyboardInterrupt, SystemExit):
        pass
