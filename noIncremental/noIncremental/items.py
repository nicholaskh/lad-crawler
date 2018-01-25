# -*- coding: utf-8 -*-
from scrapy.conf import settings
import scrapy

class BroadcastItem(scrapy.Item):
    collection = settings['COLLECTION_BROADCAST']
    module = scrapy.Field() # 模块名称
    className = scrapy.Field() # 分类名称
    title = scrapy.Field() # 标题
    source = scrapy.Field() # 来源
    sourceUrl = scrapy.Field() # 来源网址
    intro = scrapy.Field() # 广播简介
    broadcast_url = scrapy.Field() # 广播url
    edition = scrapy.Field() # 广播集数
    # 下面的写在pipeline里
    random_num = scrapy.Field()  # 随机数
    visitNum = scrapy.Field()  # 阅读量
    commnetNum = scrapy.Field()  # 评论数量
    thumpsubNum = scrapy.Field()  # 点赞数量

class VideoItem(scrapy.Item):
    collection = settings['COLLECTION_VIDEO']
    module = scrapy.Field() # 模块名称
    className = scrapy.Field() # 分类名称
    title = scrapy.Field() # 名字
    source = scrapy.Field() # 来源
    sourceUrl = scrapy.Field() # 来源网址
    url = scrapy.Field() # 视频
    poster = scrapy.Field() # poster图片
    edition = scrapy.Field()  # 视频级数
    #下面的写在pipeline里
    num = scrapy.Field() # 随机数
    visitNum = scrapy.Field() #阅读量
    shareNum = scrapy.Field() #转发量
    commnetNum = scrapy.Field() #评论数量
    thumpsubNum = scrapy.Field() #点赞数量
    collectNum = scrapy.Field() #收藏数量