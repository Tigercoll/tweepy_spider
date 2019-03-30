"""
处理数据生成csv文件 格式 username1  username2 是否关注
"""
import pandas as pd
from tweepy_api import get_api
import time

class ProcessData(object):
    def __init__(self):
        self.api = get_api()

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
                    with open('following.csv', 'a') as f:
                        f.write('{},{},{}\n'.format(user_1, user_2, is_follow))
                except Exception as e:
                    print(e)
                    # 由于国内这边网络问题常常链接超时,
                    # 如果报错就等待15分钟
                    # time.sleep(15*60+30)


# 预处理
# read the entire file into a python array
with open('python.json', 'r') as f:
    data = f.readlines()
# 将数据放入datafrom
data = map(lambda x: x.rstrip(), data)

data_json_str = "[" + ','.join(data) + "]"

data_df = pd.read_json(data_json_str)

# 获取用户名
# print(data_df['user_name'])
process_data = ProcessData()
# 获取用户是否关注 A关注B 为 1  否则为0
# process_data.get_follow(data_df)

# 获取关注信息绘制图
# import matplotlib.pyplot as plt
# import networkx as nx
# def draw_picture(filename):
#     # 打开保存的csv图片
#     with open(filename, 'r') as f:
#         # 定义两个列表,有关注的列表跟没有关注的列表
#         follow_list = []
#         unfollow_list = []
#         for line in f:
#             # 获取是否关注
#             is_follow = line.strip().split(',')[2]
#             # 判断关注
#             if is_follow == '1':
#                 follow_list.append(line.strip().split(','))
#             else:
#                 unfollow_list.append(line.strip().split(',')[0])
#     # networkx绘制关系有向图的神器,下次再讲
#     DG = nx.DiGraph()
#     # 添加节点
#     # 是一个列表
#     DG.add_nodes_from(unfollow_list)
#     # 添加有向节点 为一个两元,或三元列表(A,B,int)表示为A到B
#     DG.add_weighted_edges_from(follow_list)
#     # 画图
#     nx.draw(DG, with_labels=True)
#     # 展示
#     plt.show()
# filename = 'following.csv'
# draw_picture(filename)


