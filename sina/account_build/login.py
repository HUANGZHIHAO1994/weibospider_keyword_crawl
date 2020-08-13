import os
import pymongo
from pymongo.errors import DuplicateKeyError
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import sys
import time
import random
from selenium import webdriver
from selenium.common.exceptions import WebDriverException
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from scrapy.http.response.html import HtmlResponse
from selenium.webdriver.chrome.options import Options


# print(os.path.abspath(os.path.join(os.path.dirname(__file__), "../..")))
# sys.path.append(os.getcwd())
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__),"../..")))
from sina.settings import LOCAL_MONGO_HOST, LOCAL_MONGO_PORT, DB_NAME

TEMPLATES_FOLDER = os.getcwd() + '/sina/account_build/templates/'

#  随机请求头设置
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

class WeiboLogin():
    def __init__(self, username, password):
        # os.system('pkill -f phantom')
        self.url = 'https://passport.weibo.cn/signin/login?entry=mweibo&r=https://weibo.cn/'
        # 这里需要修改，给出自己电脑phantomjs.exe的位置
        headers = {}
        headers['User-Agent'] = random.choice(USER_AGENTS)
        chrome_options = Options()
        # headers = random.choice(USER_AGENTS)
        chrome_options.add_argument('--user-agent={}'.format(headers))  # 设置请求头的User-Agent
        chrome_options.add_argument('--blink-settings=imagesEnabled=false')  # 不加载图片, 提升速度
        chrome_options.add_argument('--headless')  # 浏览器不提供可视化页面
        chrome_options.add_argument('--disable-gpu')
        chrome_options.add_argument('--no-sandbox')
        chrome_options.add_argument('--disable-dev-shm-usage')

        self.browser = webdriver.Chrome(chrome_options=chrome_options)
        self.browser.maximize_window()
        # self.browser = webdriver.PhantomJS()
        # self.browser.set_window_size(1050, 840)
        self.wait = WebDriverWait(self.browser, 20)
        self.username = username
        self.password = password

    def open(self):
        """
        打开网页输入用户名密码并点击
        :return: None
        """
        self.browser.get(self.url)
        username = self.wait.until(EC.presence_of_element_located((By.ID, 'loginName')))
        password = self.wait.until(EC.presence_of_element_located((By.ID, 'loginPassword')))
        submit = self.wait.until(EC.element_to_be_clickable((By.ID, 'loginAction')))
        username.send_keys(self.username)
        password.send_keys(self.password)
        submit.click()

    def run(self):
        """
        破解入口
        :return:
        """
        self.open()
        WebDriverWait(self.browser, 30).until(
            EC.title_is('我的首页')
        )
        cookies = self.browser.get_cookies()
        cookie = [item["name"] + "=" + item["value"] for item in cookies]
        cookie_str = '; '.join(item for item in cookie)
        self.browser.quit()
        return cookie_str


def login_weibo():
    print("当前时间为：{}".format(time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())))
    # file_path = './account.txt'
    # print(os.getcwd())
    # print("*" * 30)
    # print(os.listdir(os.getcwd()))
    # print(open("account.txt").read())
    file_path = 'account.txt'
    with open(file_path, 'r') as f:
        lines = f.readlines()
        # print(lines)
    mongo_client = pymongo.MongoClient(LOCAL_MONGO_HOST, LOCAL_MONGO_PORT)
    collection = mongo_client[DB_NAME]["account"]
    count = 0
    f = open("problem_account.txt", "r+")
    f.truncate()
    f.close()
    for line in lines:
        count += 1
        start = time.perf_counter()
        line = line.strip()
        username = line.split('----')[0]
        password = line.split('----')[1]
        print('=' * 10 + username + '=' * 10)
        try:
            cookie_str = WeiboLogin(username, password).run()
        except Exception as e:
            f = open("problem_account.txt", "a+")
            f.write(line + '\n')
            f.close()
            print(e)
            continue
        end = time.perf_counter()
        print('获取第{}个账号的cookie成功，耗时：{}'.format(count, end - start))
        print('Cookie:', cookie_str)
        try:
            collection.insert_one(
                {"_id": username, "password": password, "cookie": cookie_str, "status": "success"})
        except DuplicateKeyError as e:
            collection.find_one_and_update({'_id': username}, {'$set': {'cookie': cookie_str, "status": "success"}})


def judge():
    while True:
        print("=" * 30)
        print("当前时间为：{}".format(time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())))
        print("现在开始判断：")
        mongo_client = pymongo.MongoClient(LOCAL_MONGO_HOST, LOCAL_MONGO_PORT)
        collection = mongo_client[DB_NAME]["account"]
        all_count = collection.count_documents({'status': 'success'})
        if all_count < 70:
            print("需重新获取cookie！！！重新获取中")
            print("=" * 30)
            try:
                login_weibo()
            except:
                continue
            time.sleep(3600)
        else:
            print("这一个小时帐号池可用账号充足，无需重新获取cookie")
            time.sleep(3600)


if __name__ == '__main__':
    # 在目录中新建一个account.txt文件，格式需要与account_sample.txt相同
    # 其实就是把www.xiaohao.shop买的账号复制到新建的account.txt文件中
    # file_path = os.getcwd() + '/sina/account_build/account.txt'
    '''
    注意长时间不运行 原cookie会失效，首次运行需要先运行login_weibo()
    '''
    login_weibo()
    judge()
