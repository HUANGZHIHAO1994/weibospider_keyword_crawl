# -*- coding: utf-8 -*-

BOT_NAME = 'sina'

SPIDER_MODULES = ['sina.spiders']
NEWSPIDER_MODULE = 'sina.spiders'

ROBOTSTXT_OBEY = False

DEFAULT_REQUEST_HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10.13; rv:61.0) Gecko/20100101 Firefox/61.0',
}

# 关闭DEBUG信息
# LOG_LEVEL ='INFO'  # 或者LOG_ENABLED = False

# CONCURRENT_REQUESTS 和 DOWNLOAD_DELAY 根据账号池大小调整 目前的参数是账号池大小为200

CONCURRENT_REQUESTS = 20

DOWNLOAD_DELAY = 0.1

DOWNLOADER_MIDDLEWARES = {
    'weibo.middlewares.UserAgentMiddleware': None,
    'scrapy.downloadermiddlewares.cookies.CookiesMiddleware': None,
    'scrapy.downloadermiddlewares.redirect.RedirectMiddleware': None,
    'sina.middlewares.UserAgentDownloadMiddleware': 100,
    'sina.middlewares.CookieMiddleware': 300,
    'sina.middlewares.RedirectMiddleware': 200,
    'sina.middlewares.IPProxyMiddleware': 400,
    'scrapy.downloadermiddlewares.httpproxy.HttpProxyMiddleware': 101,
}

ITEM_PIPELINES = {
    'sina.pipelines.MongoDBPipeline': 300,
}

# MongoDb 配置

LOCAL_MONGO_HOST = '127.0.0.1'
LOCAL_MONGO_PORT = 27017
DB_NAME = 'Sina'


# IP
DOWNLOAD_TIMEOUT = 5

RETRY_TIMES = 5

DEPTH_LIMIT = 2
