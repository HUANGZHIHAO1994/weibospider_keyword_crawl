import requests
import json
import time
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import Select
from selenium.webdriver.common.keys import Keys

from playsound import playsound

#（此处要修改）
PROXY_URL = 'http://www.zdopen.com/ShortProxy/GetIP/?api=201905291017397242&akey=43934b59dc12fa0a&count=5&order=1&type=3'

while True:
    try:
        response = requests.get(PROXY_URL)
        if response.status_code == 200:
            text = response.text
            print('重新获取了一堆代理：', text)
            result = json.loads(text)
            f = open("proxy.txt", "w")
            if result['code'] == '10001':
                for i in range(len(result['data']['proxy_list'])):
                    data = result['data']['proxy_list'][i]
                    ip = data['ip']
                    port = data['port']
                    ip_proxy = '{}:{}'.format(ip, port)
                    f.write(ip_proxy + '\n')
            f.close()

        else:
            # 返回非200说明登入记住密码失效。。。
            url = "http://ip.zdaye.com/Users/Login.html"
            driver = webdriver.Chrome()
            # chrome_options = Options()
            # chrome_options.add_argument('--headless')
            # chrome_options.add_argument('--disable-gpu')
            # driver = webdriver.Chrome(chrome_options=chrome_options)
            driver.get(url)
            WebDriverWait(driver, 100, 0.5).until(
                EC.presence_of_element_located((By.XPATH, "//div")))
            try:
                input1 = driver.find_element_by_name("usernamePH")
                input1.send_keys("账号")     # 输入登入账号（此处要修改）
                time.sleep(0.1)

                input2 = driver.find_element_by_name("passwordPH")
                input2.send_keys("密码")     # 输入登入密码（此处要修改）
                input2.send_keys(Keys.ENTER)

                WebDriverWait(driver, 100, 0.5).until(
                    EC.presence_of_element_located((By.XPATH, "//div[@class='display']//a[@href='ShortProxy/']")))

                input4 = driver.find_element_by_xpath(
                    "//div[@class='display']//a[@href='ShortProxy/']")
                input4.click()
                time.sleep(0.1)

                input5 = driver.find_element_by_xpath(
                    "//a[@href='CreateAPI.html?api=201905291017397242']")
                input5.click()
                time.sleep(0.1)

                selectTag = Select(driver.find_element_by_name("type"))
                selectTag.select_by_value("3")
                time.sleep(0.1)

                button = driver.find_elements_by_xpath("//button")[1]
                button.click()
                time.sleep(0.1)
                PROXY_URL = driver.find_element_by_id("thisURL").text    #  重新获取PROXY_URL
                time.sleep(0.1)
            except:
                pass

            continue
    except Exception as e:
        playsound('xiyouji.mp3')     #  此处可以更换音乐
        print(e)
    time.sleep(12)      #  每隔12s更新IP池
