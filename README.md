## Tweepy库通过关键字分析Twitter数据

#### 1.收集数据

第一步,你需要去注册你的Twitter,获取你的访问权限.

```python
consumer_key ='YOUR-CONSUMER-KEY'
consumer_secret ='YOUR-CONSUMER-SECRET'
access_token ='YOUR-ACCESS-TOKEN'
access_secret='YOUR-ACCESS-SECRET'
```

要获取数据,你必须登录到twitter,这里使用tweepy的OAuthHandler类

```python
import tweepy

# 获取key跟secret
consumer_key ='YOUR-CONSUMER-KEY'
consumer_secret ='YOUR-CONSUMER-SECRET'
access_token ='YOUR-ACCESS-TOKEN'
access_secret='YOUR-ACCESS-SECRET'
auth = tweepy.OAuthHandler(consumerKey,consumerSecret)
auth.set_access_token(accessToken,accessTokenSecret)
# 国内的朋友记得添加代理proxy,我这边用的是Shadowsocks
api=tweepy.API(auth,proxy='127.0.0.1:1080')
```

官网提供我们几个获取推文的方法

home_timeline()函数,拉取你的Twitter动态中最新的推文

```python
public_tweets = api.home_timeline()
for tweet in public_tweets:
     # text方法获取文本信息
    print tweet.text
```

![](<https://github.com/Tigercoll/my_picturelib/raw/master/tweepy/1.png>)

```python
print(type(public_tweets[0]))
print(public_tweets[0])
# 打印返回一个Status对象,从中我们获取我们需要的存入json文件就可以了.
```

其中的很多函数,可以参考tweepy <http://docs.tweepy.org/en/stable/api.html>

流媒体

如果我们要“保持连接”，并收集所有关于特定事件将会出现的tweets，流API就是我们所需要的。

In Tweepy, an instance of **tweepy.Stream** establishes a streaming session and routes messages to **StreamListener** instance. The **on_data** method of a stream listener receives all messages and calls functions according to the message type. The default **StreamListener** can classify most common twitter messages and routes them to appropriately named methods, but these methods are only stubs.

```python
# 创建StreamListener
class MyStreamListener(tweepy.StreamListener):
    # 处理数据
    def on_status(self, status):
        print(status.text)
    # 处理错误
    def on_error(self, status_code):
        if status_code == 420:
            # returning False in on_data disconnects the stream
            return False
            # returning non-False reconnects the stream, with backoff
# 创建流对象
myStreamListener = MyStreamListener()
# 国内需要代理
proxies = {'http': 'http://localhost:1080', 'https': 'http://localhost:1080'}
myStream = tweepy.Stream(auth = api.auth, listener=myStreamListener,proxies=proxies)
# 启动流track=['python']检索关键字,is_async 是否异步
myStream.filter(track=['python'],languages=["en"],is_async=True)
```

重写on_status方法 处理数据,

通过推特官方提供的api文档获取返回值具体可查看<https://developer.twitter.com/en/docs/tweets/data-dictionary/overview/tweet-object>

```python
 def on_status(self, status):
        data_dict={}
        # 获取json数据,获取的只是个字典方便我们预处理,留下想要的字段
        data = status._json
        # 文章ID
        data_dict['id_str'] = data['id_str']
        # 文章内容
        data_dict['text'] = data['text']
        # 时间
        data_dict['date'] = data['created_at']
        # 发布坐标
        data_dict['coordinates'] = data['coordinates']
        # hashtags
        data_dict['hashtags'] = data['entities']['hashtags']
        # 喜欢度
        data_dict['favorited'] = data['favorited']
        # 用户id
        data_dict['user_id_str'] = data['user']['id_str']
        #用户名
        data_dict['user_name'] = data['user']['name']
        # 用户位置
        data_dict['user_location'] = data['user']['location']
        # 写入到json文件
        print(data_dict)
        try:
            with open('python.json','a') as f:
                f.write(json.dumps(data_dict))
                f.write('\n')
            return True
        except Exception as e:
            print('error:{e}'.format(e=e))
        return True
# 这里需要一直爬取 所以重写on_error
 def on_error(self, status_code):
        print(status_code)
        return True
```

等有了数据 我们就可以初步处理了.

#### 2.预处理数据

获取关注信息:

```python
# 预处理
# read the entire file into a python array
# 用到了pandas库
with open('python.json', 'r') as f:
    data = f.readlines()
# 将数据放入datafrom
data = map(lambda x: x.rstrip(), data)
data_json_str = "[" + ','.join(data) + "]"
data_df = pd.read_json(data_json_str)
# 因为我们存的时候是一行条json数据,所以需要预处理一下
```

```python
def get_follow(self,data_df):
     """# 获取用户是否关注 A关注B 为 1  否则为0"""
    for user_1 in data_df['screen_name']:
        for user_2 in data_df['screen_name']:
            is_follow = 0
            if user_1 == user_2:
                continue
            try:
                status = self.api.show_friendship(source_screen_name=user_1, target_screen_name=user_2)
                print(status)
                if status[0].following:
                    is_follow = 1
                #保存为csv文件
                with open('following.csv', 'a') as f:
                    f.write('{},{},{}\n'.format(user_1, user_2, is_follow))
            except Exception as e:
                print(e)
                # 由于国内这边网络问题常常链接超时,
                # 如果报错就等待15分钟
                # time.sleep(15*60+30)
```

由于这边是遍历所有名字,所以只需要知道A是否关注B 就可以了.

#### 3.绘制有向图

这里用到两个库matplotlib跟networkx

```python
# 获取关注信息绘制图
import matplotlib.pyplot as plt
import networkx as nx
# 打开保存的csv图片
with open('following.csv','r') as f:
    # 定义两个列表,有关注的列表跟没有关注的列表
    follow_list = []
    unfollow_list=[]
    for line in f:
        # 获取是否关注
        is_follow = line.strip().split(',')[2]
        # 判断关注
        if is_follow=='1':
            follow_list.append(line.strip().split(','))
        else:
            unfollow_list.append(line.strip().split(',')[0])
# networkx绘制关系有向图的神器,下次再讲
DG = nx.DiGraph()
# 添加节点
# 是一个列表
DG.add_nodes_from(unfollow_list)
# 添加有向节点 为一个两元,或三元列表(A,B,int)表示为A到B
DG.add_weighted_edges_from(follow_list)
# 画图
nx.draw(DG, with_labels=True)
# 展示
plt.show()


```

由于数据较少,且是抓取关键词,所以用户之间关注度不高,且基本为认证账号

![](<https://github.com/Tigercoll/my_picturelib/raw/master/tweepy/2.png>)

