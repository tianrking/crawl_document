
"""
立项     模块

采集房源信息   链家网
xpath 筛选数据  选取标签

批量的数据采集   几百的数据   几十万



"""
import requests    # 发生网络请求的工具包   第三方库
from lxml import etree  #  转换数据对象


url = 'https://cs.lianjia.com/ershoufang/pg2/'
response = requests.get(url)
# print(response.text)
data = etree.HTML(response.text)
# print(data)
info_list = data.xpath('//div[@class="info clear"]')  # 获取列表数据
# print(info_list)
for div in info_list:
    title = div.xpath('.//div[@class="title"]/a/text()')[0]
    position = div.xpath('.//div[@class="flood"]/div/a[2]/text()')[0]
    address = div.xpath('.//div[@class="address"]/div/text()')[0]
    follow = div.xpath('.//div[@class="followInfo"]/text()')[0]
    total_price = div.xpath('.//div[@class="priceInfo"]/div[1]/span/text()')[0]
    unit_price = div.xpath('.//div[@class="priceInfo"]/div[2]/span/text()')[0]

    print({'title': title, 'position': position, 'address': address, 'follow': follow, 'total_price': total_price,
           'unit_price': unit_price})






