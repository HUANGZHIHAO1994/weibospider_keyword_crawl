<div align="left">
    <img src='http://chuantu.xyz/t6/740/1596860921x1033347913.jpg' height="50" width="50" >
 </div>





## 0.  特别鸣谢

这个微博爬虫是对现有的爬虫框架的部分环节进行优化，在此首先对该新浪微博爬虫原作者作者表示感谢！该作者github连接如下所示：

[https://github.com/nghuyong/WeiboSpider](https://github.com/nghuyong/WeiboSpider)



## 1.  优化说明

1. **关键词爬取：**

  原作者是基于某些微博用户的爬取逻辑，这里修改**weibo_spider.py** 增加基于<u>**关键词**</u>搜索爬取方法

2. **帐号池管理：**

   ① 在 **login.py** 中增加：   <u>每小时检查微博账号cookie池</u>

   （因为作者在进行爬虫时发现新浪微博封账号并非永封，及时更新帐号池状态很有必要）

   ② 在 **login.py** 中增加：   <u>增加账号获取进度</u>

   （本次修改爬取时用了110个账号，大约全部获取需要20分钟，因此增加账号获取cookie进度提高用户体验）

   ③ 在 **login.py** 中增加：   <u>获取cookie失败账号</u>

   （将每次获取失败的账号写入 **problem_account.txt**）

3. **代理IP实例化：**

   本次优化介绍如何使用付费ip代理：<u>芝麻代理和站大爷</u>

   首先，最适用微博爬虫的代理ip形式是：<u>包天不限量，存活期无所谓</u>

   ① 芝麻代理： 按次提取0.04元/次 ，或者包周98元，但每天上限700个ip，因此需要通过 response.status == 418 判断是否需要更换ip，但有一些封ip的情况 response.status == 200，因此使用芝麻代理爬虫会错过部分信息，具体修改 **middlewares.py** 和 增加 **models.py**

   http://h.zhimaruanjian.com/getapi/

   ② 站大爷（推荐）：包天25元，每次最大提取5个ip，10秒可重新提取一次，因此增加 **proxy.py** 来每隔15秒更新ip池（**proxy.txt**），并对 **middlewares.py** 稍作修改

   http://ip.zdaye.com/Users/ShortProxy/

   PS：在**proxy.py** 新增断网人工检测，断网时或者部分异常情况时，有时候需要重新刷新站大爷那边的链接，因此抓取该类异常并播放音乐提醒进行人工检测

4. **超大评论数处理：**

   评论数大于10000的微博爬取时容易影响爬虫进度，并且一般不是明星广告微博就是十分重要的微博，因此适合单独分析。在**weibo_spider.py**  中增加判断，将评论数大于10000的微博url写入**comment_url.txt**

5. **增加断点续存机制：**

   在  **weibo_spider.py**  中增加判断（从某关键词断开的时间处进行爬取）

   若断开：在mongo数据库中通过时间排序方式查找关键词断开的日期，如“科技”关键词在10/25/2018日断开，①删除**keyword.txt**文档中“科技”之前的关键词②修改程序date3中的日期③在程序约48行处将关键词改为“科技”

6. **其余细节：**

   如爬取时间调整为人类可读的非计算机时间



# 2.  使用说明

1. **按照account_sample.txt将微博账号写入account.txt，运行login.py**

2. **从站大爷获取代理ip提取链接并修改proxy.py中的PROXY_URL和帐号密码，运行proxy.py（选择站大爷短效优质代理，然后生成提取连接）**

   http://ip.zdaye.com/Users/ShortProxy/

3. **修改key_words.txt文件，不同关键词通过"；"（中文格式分号）分割**

4. **修改weibo_spider.py中的爬取期间**（比如想爬2018年整一年的微博数据在date1处：01/01/2018', '12/31/2018）

5. **运行start.py**

# 3.  爬取结果示例

微博内容示例

<div>
    <img
src='https://github.com/HUANGZHIHAO1994/weibospider-keyword/blob/master/weibospider2.0/images/content_sample.png?raw=true'
         >
</div>

微博评论示例

<div>
    <img
src='https://github.com/HUANGZHIHAO1994/weibospider-keyword/blob/master/weibospider2.0/images/comment_sample.png?raw=true'     
         >
</div>







