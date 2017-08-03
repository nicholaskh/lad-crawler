# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# http://doc.scrapy.org/en/latest/topics/items.html

import scrapy


class LadItem(scrapy.Item):

    title = scrapy.Field()
    news_type = scrapy.Field()
    time = scrapy.Field()
    text = scrapy.Field()
    city = scrapy.Field()

class YangshengItem(scrapy.Item):

    web = scrapy.Field()
    title = scrapy.Field()
    yangsheng_type = scrapy.Field()
    time = scrapy.Field()
    text = scrapy.Field()

class VideoItem(scrapy.Item):
    module = scrapy.Field() # 模块
    video_name = scrapy.Field() # 视频名称
    video_link = scrapy.Field() # 视频链接

class YangshengwangItem(scrapy.Item):
    module = scrapy.Field() # 模块
    class_name = scrapy.Field() # 分类名称
    class_num = scrapy.Field() # 分类级别
    specific_name = scrapy.Field() # 分类上级名称
    title = scrapy.Field() # 标题
    source = scrapy.Field() # 来源
    source_url = scrapy.Field() # 来源网址
    image_urls = scrapy.Field() # 图片的链接
    images = scrapy.Field() # 图片
    time = scrapy.Field() # 时间
    text = scrapy.Field() # 文本
