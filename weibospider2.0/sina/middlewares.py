# encoding: utf-8
import random
import pymongo
from sina.settings import LOCAL_MONGO_PORT, LOCAL_MONGO_HOST, DB_NAME

from twisted.internet.defer import DeferredLock
import requests
from sina.models import ProxyModel
import json
from twisted.internet.error import TimeoutError

class CookieMiddleware(object):
    """
    每次请求都随机从账号池中选择一个账号去访问
    """

    def __init__(self):
        client = pymongo.MongoClient(LOCAL_MONGO_HOST, LOCAL_MONGO_PORT)
        self.account_collection = client[DB_NAME]['account']

    def process_request(self, request, spider):
        all_count = self.account_collection.find({'status': 'success'}).count()
        if all_count == 0:
            raise Exception('当前账号池为空')
        random_index = random.randint(0, all_count - 1)
        random_account = self.account_collection.find({'status': 'success'})[random_index]
        request.headers.setdefault('Cookie', random_account['cookie'])
        request.meta['account'] = random_account


class RedirectMiddleware(object):
    """
    检测账号是否正常
    302 / 403,说明账号cookie失效/账号被封，状态标记为error
    418,偶尔产生,需要再次请求
    """

    def __init__(self):
        client = pymongo.MongoClient(LOCAL_MONGO_HOST, LOCAL_MONGO_PORT)
        self.account_collection = client[DB_NAME]['account']

    def process_response(self, request, response, spider):
        http_code = response.status
        if http_code == 302 or http_code == 403:
            self.account_collection.find_one_and_update({'_id': request.meta['account']['_id']},
                                                        {'$set': {'status': 'error'}}, )
            print("更换账号成功")
            return request
        elif http_code == 418:
            spider.logger.error('ip 被封了!!!请更换ip,或者停止程序...')
            return request
        elif http_code != 200:
            self.account_collection.find_one_and_update({'_id': request.meta['account']['_id']},
                                                        {'$set': {'status': 'error'}}, )
            print("其他异常发生的情况下，更换账号成功: ")
            return request
        else:
            return response


class IPProxyMiddleware(object):
    # 站大爷包天版本，先运行proxy提取ip
    def fetch_proxy(self):
        # 如果需要加入代理IP，请重写这个函数
        # 这个函数返回一个代理ip，'ip:port'的格式，如'12.34.1.4:9090'
        f = open("proxy.txt")
        s = f.read()
        s = s.split('\n')
        index = random.randint(0, len(s) - 1)
        random_ip = s[index]
        f.close()
        return random_ip

    def process_request(self, request, spider):
        proxy_data = self.fetch_proxy()
        if proxy_data:
            current_proxy = f'http://{proxy_data}'
            spider.logger.debug(f"当前代理IP:{current_proxy}")
            request.meta['proxy'] = current_proxy

# class IPProxyMiddleware(object):
#     # 芝麻代理包周或按次提取版本（此处要修改PROXY_URL）
#     PROXY_URL = '此处要修改PROXY_URL'
#
#     def __init__(self):
#         super(IPProxyMiddleware, self).__init__()
#         self.current_proxy = None
#         self.lock = DeferredLock()
#
#     def process_request(self, request, spider):
#         if 'proxy' not in request.meta or self.current_proxy.is_expiring:
#             # 请求代理
#             self.update_proxy()
#
#         request.meta['proxy'] = self.current_proxy.proxy
#
#     def process_response(self, request, response, spider):
#         if response.status == 418:
#             if not self.current_proxy.blacked:
#                 self.current_proxy.blacked = True
#             print('%s这个代理被加入黑名单了' % self.current_proxy.ip)
#             self.update_proxy()
#             return request
#         # 如果是正常的，那么要记得返回response
#         # 如果不返回，那么这个resposne就不会被传到爬虫那里去
#         # 也就得不到解析
#         return response
#
#     def update_proxy(self):
#         self.lock.acquire()
#         if not self.current_proxy or self.current_proxy.is_expiring or self.current_proxy.blacked:
#             response = requests.get(self.PROXY_URL)
#             text = response.text
#             print('重新获取了一个代理：', text)
#             result = json.loads(text)
#             if len(result['data']) > 0:
#                 data = result['data'][0]
#                 proxy_model = ProxyModel(data)
#                 self.current_proxy = proxy_model
#         self.lock.release()

class UserAgentDownloadMiddleware(object):
    # user-agent随机请求头中间件
    USER_AGENTS = [
        'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/70.0.3538.77 Safari/537.36',
        'Mozilla/5.0 (Windows NT 6.2; WOW64) AppleWebKit/537.36 (KHTML like Gecko) Chrome/44.0.2403.155 Safari/537.36',
        'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/41.0.2227.0 Safari/537.36',
        'Mozilla/5.0 (Windows NT 6.1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/41.0.2228.0 Safari/537.36',
        'Mozilla/5.0 (Windows NT 5.1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/41.0.2224.3 Safari/537.36',
        'Mozilla/5.0 (Windows NT 10.0) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/40.0.2214.93 Safari/537.36',
        'Mozilla/4.0 (compatible; MSIE 8.0; Windows NT 6.1; Trident/4.0; Avant Browser; SLCC2; .NET CLR 2.0.50727; .NET CLR 3.5.30729; .NET CLR 3.0.30729; Media Center PC 6.0)',
        'Mozilla/5.0 (X11; Linux i686; rv:64.0) Gecko/20100101 Firefox/64.0',
        'Mozilla/5.0 (X11; Linux i586; rv:63.0) Gecko/20100101 Firefox/63.0',
        'Mozilla/5.0 (Macintosh; U; Intel Mac OS X 10.10; rv:62.0) Gecko/20100101 Firefox/62.0'
    ]
    def process_request(self,request,spider):
        user_agent = random.choice(self.USER_AGENTS)
        request.headers['User-Agent'] = user_agent