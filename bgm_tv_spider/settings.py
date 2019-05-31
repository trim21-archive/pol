import os
import platform
import sys

# Override the default request headers:
import scrapy

# pymysql.install_as_MySQLdb()
# Scrapy settings for tutorial project
#
# For simplicity, this file contains only settings considered important or
# commonly used. You can find more settings consulting the documentation:
#
#     https://doc.scrapy.org/en/latest/topics/settings.html
#     https://doc.scrapy.org/en/latest/topics/downloader-middleware.html
#     https://doc.scrapy.org/en/latest/topics/spider-middleware.html

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

# Configure a delay for requests for the same website (default: 0)
# See https://doc.scrapy.org/en/latest/topics/settings.html#download-delay
# See also autothrottle settings and docs
# DOWNLOAD_DELAY = 0.1
# The download delay setting will honor only one of:
# CONCURRENT_REQUESTS_PER_DOMAIN = 16
# CONCURRENT_REQUESTS_PER_IP = 16

# Disable cookies (enabled by default)
# COOKIES_ENABLED = False

# Disable Telnet Console (enabled by default)
# TELNETCONSOLE_ENABLED = False

DEFAULT_REQUEST_HEADERS = {
    # 'Accept-Encoding': 'gzip, deflate, br',
    'User-Agent': f'bgm_tv_spider-ip-viewer bgm_tv_spider '
    f'scrapy {scrapy.__version__} python {sys.version} '
    f'see github.com/Trim21/bgm_tv_spider-ip-viewer/ for more details',
    'Accept-Encoding': 'gzip, deflate',
}

# Enable or disable bgm_tv_spider middlewares
# See https://doc.scrapy.org/en/latest/topics/spider-middleware.html
SPIDER_MIDDLEWARES = {
    #    'tutorial.middlewares.TutorialSpiderMiddleware': 543,
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
    # 'scrapy.downloadermiddlewares.downloadtimeout.DownloadTimeoutMiddleware
    # ': None,
    # 'scrapy.downloadermiddlewares.defaultheaders.DefaultHeadersMiddleware'
    # : None,
    # 'scrapy.downloadermiddlewares.retry.RetryMiddleware'
    # : None,
    # 'scrapy.downloadermiddlewares.httpcompression.HttpCompressionMiddleware
    # ': None,
    # 'scrapy.downloadermiddlewares.redirect.RedirectMiddleware'
    # : None,
    # 'scrapy.downloadermiddlewares.stats.DownloaderStats'
    # : None,
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
    # 'bgm_tv_spider.pipelines.MongoDBPipeline': 300,
    'bgm_tv_spider.pipelines.MysqlPipeline': 400,
}
# Enable and configure the AutoThrottle extension (disabled by default)
# See https://doc.scrapy.org/en/latest/topics/autothrottle.html
AUTOTHROTTLE_ENABLED = True
# The initial download delay
AUTOTHROTTLE_START_DELAY = 1
# The maximum download delay to be set in case of high latencies
AUTOTHROTTLE_MAX_DELAY = 5
# The average number of requests Scrapy should be sending in parallel to
# each remote server
AUTOTHROTTLE_TARGET_CONCURRENCY = 8
# Enable showing throttling stats for every response received:
AUTOTHROTTLE_DEBUG = True
DOWNLOAD_TIMEOUT = 30
# Enable and configure HTTP caching (disabled by default)
# See https://doc.scrapy.org/en/latest/topics/downloader-middleware.html
# #httpcache-middleware-settings
HTTPCACHE_ENABLED = True
HTTPCACHE_EXPIRATION_SECS = 60 * 60 * 24 * 14  # 2 weeks
HTTPCACHE_DIR = 'httpcache'
HTTPCACHE_GZIP = True
HTTPCACHE_STORAGE = 'scrapy.extensions.httpcache.DbmCacheStorage'
# HTTPCACHE_IGNORE_HTTP_CODES = []
if 'windows' in platform.platform().lower():
    MYSQL_HOST = 'bgmi.acg.tools'
    MYSQL_DBNAME = 'bgm_ip_viewer'
    MYSQL_USER = 'root'
    MYSQL_PASSWORD = 'password'
else:
    MYSQL_HOST = os.environ.get('MYSQL_HOST')
    MYSQL_DBNAME = os.environ.get('MYSQL_DBNAME')
    MYSQL_USER = os.environ.get('MYSQL_USER')
    MYSQL_PASSWORD = os.environ.get('MYSQL_PASSWORD')
    # import scrapy.extensions.httpcache
    HTTPCACHE_STORAGE = 'scrapy.extensions.httpcache.LeveldbCacheStorage'
