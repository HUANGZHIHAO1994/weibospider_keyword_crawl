import os
import pymongo
from pymongo.errors import DuplicateKeyError
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import sys
import time

sys.path.append(os.getcwd())
from sina.settings import LOCAL_MONGO_HOST, LOCAL_MONGO_PORT, DB_NAME

TEMPLATES_FOLDER = os.getcwd() + '/sina/account_build/templates/'


class WeiboLogin():
    def __init__(self, username, password):
        os.system('pkill -f phantom')
        self.url = 'https://passport.weibo.cn/signin/login?entry=mweibo&r=https://weibo.cn/'
        # 这里需要修改，给出自己电脑phantomjs.exe的位置
        self.browser = webdriver.PhantomJS(executable_path=r'D:\phantomjs-2.1.1-windows\bin\phantomjs.exe')
        self.browser.set_window_size(1050, 840)
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
    file_path = './account.txt'
    with open(file_path, 'r') as f:
        lines = f.readlines()
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
            collection.insert(
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
        all_count = collection.find({'status': 'success'}).count()
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
