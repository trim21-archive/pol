import platform

BOT_NAME = 'bgm_tv_spider'
LOG_LEVEL = 'INFO'

SPIDER_MODULES = ['bgm_tv_spider.spiders']
NEWSPIDER_MODULE = 'bgm_tv_spider.spiders'

# Crawl responsibly by identifying yourself (and your website) on the user-agent
# USER_AGENT = 'tutorial (+http://www.yourdomain.com)'

# Obey robots.txt rules
ROBOTSTXT_OBEY = False
FEED_EXPORT_ENCODING = 'utf-8'

# Configure maximum concurrent requests performed by Scrapy (default: 16)
CONCURRENT_REQUESTS = 16

# Override the default request headers:
DEFAULT_REQUEST_HEADERS = {
    # 'Accept-Encoding': 'gzip, deflate, br',
    'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) '
    'AppleWebKit/537.36 (KHTML, like Gecko) Chrome/72.0.3626.121 Safari/537.36',
    # 'User-Agent': f'bgm_tv_spider-ip-viewer bgm_tv_spider '
    # f'scrapy {scrapy.__version__} python {sys.version} '
    # f'see github.com/Trim21/bgm_tv_spider-ip-viewer/ for more details',
    'Accept-Encoding': 'gzip, deflate',
}

# Enable or disable bgm_tv_spider middlewares
# See https://doc.scrapy.org/en/latest/topics/spider-middleware.html
SPIDER_MIDDLEWARES = {
    #    'tutorial.middlewares.TutorialSpiderMiddleware': 543,
    'bgm_tv_spider.middlewares.DelayedRequestsMiddleware': 233,
    'scrapy.spidermiddlewares.httperror.HttpErrorMiddleware': None,
    'scrapy.spidermiddlewares.offsite.OffsiteMiddleware': None,
    'scrapy.spidermiddlewares.referer.RefererMiddleware': None,
    # 'scrapy.spidermiddlewares.urllength.UrlLengthMiddleware': None,
    'scrapy.spidermiddlewares.depth.DepthMiddleware': None,
}
# DOWNLOAD_HANDLERS = {
#     'https': 'scrapy.core.downloader.handlers.http10.HTTP10DownloadHandler',
# }
# Enable or disable downloader middlewares
# See https://doc.scrapy.org/en/latest/topics/downloader-middleware.html
DOWNLOADER_MIDDLEWARES = {
    # 'scrapy.downloadermiddlewares.downloadtimeout.DownloadTimeoutMiddleware':
    # None,
    # 'scrapy.downloadermiddlewares.defaultheaders.DefaultHeadersMiddleware':
    # None,
    # 'scrapy.downloadermiddlewares.httpcompression.HttpCompressionMiddleware':
    # None,
    # 'scrapy.downloadermiddlewares.redirect.RedirectMiddleware': None,
    # 'scrapy.downloadermiddlewares.stats.DownloaderStats': None,
    # 'scrapy.downloadermiddlewares.retry.RetryMiddleware': None,
    'scrapy.downloadermiddlewares.redirect.MetaRefreshMiddleware': None,
    'scrapy.downloadermiddlewares.httpauth.HttpAuthMiddleware': None,
    'scrapy.downloadermiddlewares.useragent.UserAgentMiddleware': None,
    'scrapy.downloadermiddlewares.cookies.CookiesMiddleware': None,
    'scrapy.downloadermiddlewares.httpproxy.HttpProxyMiddleware': None,
}

# Enable or disable extensions
# See https://doc.scrapy.org/en/latest/topics/extensions.html
EXTENSIONS = {
    'scrapy.extensions.telnet.TelnetConsole': None,
}

# Configure item pipelines
# See https://doc.scrapy.org/en/latest/topics/item-pipeline.html
ITEM_PIPELINES = {
    'bgm_tv_spider.pipelines.MysqlPipeline': 400,
}
# DEPTH_PRIORITY = 50
RETRY_TIMES = 5
# Enable and configure the AutoThrottle extension (disabled by default)
# See https://doc.scrapy.org/en/latest/topics/autothrottle.html
AUTOTHROTTLE_ENABLED = True
# The initial download delay
AUTOTHROTTLE_START_DELAY = 10
# The maximum download delay to be set in case of high latencies
AUTOTHROTTLE_MAX_DELAY = 30
# The average number of requests Scrapy should be sending in parallel to
# each remote server
AUTOTHROTTLE_TARGET_CONCURRENCY = 8
# Enable showing throttling stats for every response received:
AUTOTHROTTLE_DEBUG = False
DOWNLOAD_TIMEOUT = 60
# Enable and configure HTTP caching (disabled by default)
# See https://doc.scrapy.org/en/latest/topics/downloader-middleware.html
# #httpcache-middleware-settings
# HTTPCACHE_IGNORE_HTTP_CODES = []

# redis-scrapy
DUPEFILTER_DEBUG = True
DUPEFILTER_CLASS = 'scrapy_redis.dupefilter.RFPDupeFilter'
DUPEFILTER_KEY = 'bgm_tv_spider:dupefilter'
# import scrapy_redis.scheduler
# scrapy_redis.scheduler.Scheduler
SCHEDULER_PERSIST = False
SCHEDULER = 'scrapy_redis.scheduler.Scheduler'
SCHEDULER_QUEUE_KEY = 'bgm_tv_spider:scheduler'
REDIS_PARAMS = {}
REDIS_START_URL_KEY = 'bgm_tv_spider:start_urls'

if 'windows' in platform.platform().lower():
    HTTPCACHE_ENABLED = True
    HTTPCACHE_EXPIRATION_SECS = 60 * 60 * 24 * 14  # 2 weeks
    HTTPCACHE_DIR = 'httpcache'
    HTTPCACHE_GZIP = True
    HTTPCACHE_STORAGE = 'scrapy.extensions.httpcache.DbmCacheStorage'

    MYSQL_HOST = 'bgmi.acg.tools'
    MYSQL_DB = 'bgm_ip_viewer'
    MYSQL_USER = 'root'
    MYSQL_PASSWORD = 'password'
    REDIS_HOST = '192.168.1.4'

else:
    from app.core import config
    HTTPCACHE_ENABLED = False
    REDIS_HOST = config.REDIS_HOST
    MYSQL_HOST = config.MYSQL_HOST
    MYSQL_DB = config.MYSQL_DB
    MYSQL_USER = config.MYSQL_USER
    MYSQL_PASSWORD = config.MYSQL_PASSWORD
    REDIS_PARAMS = {'password': config.REDIS_PASSWORD}
