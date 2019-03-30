"""
根据关键字获取推特数据
"""
import json
import tweepy
from tweepy_api import get_api
api = get_api()
# public_tweets = api.search(q='python',count=1)
# # print(type(public_tweets[0]))
# # print(public_tweets[0])
# for tweet in public_tweets:
#     # text方法获取文本信息
#     print(tweet.text)
#     print(tweet.entities)
#     print(tweet.user)
#     print(tweet.id)
#     print(tweet.hashtags)
#
# 创建StreamListener
class MyStreamListener(tweepy.StreamListener):
    # 处理数据
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
        data_dict['user_id'] = data['user']['id']
        #用户名 需要screen_name
        data_dict['screen_name'] = data['user']['screen_name']
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

    # 处理错误
    def on_error(self, status_code):
        print(status_code)
        return True
            # returning False in on_data disconnects the stream

            # returning non-False reconnects the stream, with backoff
# 创建流对象
myStreamListener = MyStreamListener()

# 国内需要代理
proxies = {'http': 'http://localhost:1080', 'https': 'http://localhost:1080'}
myStream = tweepy.Stream(auth = api.auth, listener=myStreamListener,proxies=proxies)

# 启动流track=['python']检索关键字,is_async 是否异步
myStream.filter(track=['python'],languages=["en"],is_async=True,encoding='utf-8')
