"""
静态数据
动态数据

结构数据      json   xml
非结构数据    html

404

小偷

数据


404

json 数据


16长度   字母开头   必须有字母数字


"""
import re

# dict1 = {'a':2}
# print(dict1)

import re   # 正则表达式
import requests
import json


headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/98.0.4758.81 Safari/537.36'
}


url = 'https://news.163.com/special/cm_guonei_03'
response = requests.get(url, headers=headers)
# print(response.text)
# data = re.findall('data_callback(.*?)', response.text)
# print(data)
data = response.text[14:-1]
for da in json.loads(data):
    title = da['title']
    print(title)
