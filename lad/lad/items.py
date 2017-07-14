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
