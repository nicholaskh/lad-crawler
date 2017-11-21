# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# http://doc.scrapy.org/en/latest/topics/items.html

import scrapy
from scrapy.conf import settings


class LadItem(scrapy.Item):
    collection = settings['COLLECTION_SECURITY']
    title = scrapy.Field()
    newsType = scrapy.Field()
    time = scrapy.Field()
    text = scrapy.Field()
    city = scrapy.Field()
    sourceUrl = scrapy.Field() # 来源网址
    is_final_child = scrapy.Field()
    next_father_url = scrapy.Field()
    sourceUrl = scrapy.Field()
    imageUrls = scrapy.Field() # 图片的链接
    num = scrapy.Field() # 随机数

class YangshengItem(scrapy.Item):
    collection = settings['COLLECTION_HEALTH']
    web = scrapy.Field()
    title = scrapy.Field()
    yangshengType = scrapy.Field()
    time = scrapy.Field()
    text = scrapy.Field()
    num = scrapy.Field() # 随机数

class VideoItem(scrapy.Item):
    collection = settings['COLLECTION_HEALTH']
    module = scrapy.Field() # 模块
    videoName = scrapy.Field() # 视频名称
    videoLink = scrapy.Field() # 视频链接
    num = scrapy.Field() # 随机数

class YangshengwangItem(scrapy.Item):
    collection = settings['COLLECTION_HEALTH']
    module = scrapy.Field() # 模块
    className = scrapy.Field() # 分类名称
    classNum = scrapy.Field() # 分类级别
    specificName = scrapy.Field() # 分类上级名称
    title = scrapy.Field() # 标题
    source = scrapy.Field() # 来源
    sourceUrl = scrapy.Field() # 来源网址
    imageUrls = scrapy.Field() # 图片的链接
    images = scrapy.Field() # 图片
    time = scrapy.Field() # 时间
    text = scrapy.Field() # 文本
    is_final_child = scrapy.Field()
    next_father_url = scrapy.Field()
    num = scrapy.Field() # 随机数
