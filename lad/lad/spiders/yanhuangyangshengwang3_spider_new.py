#coding=utf-8
import scrapy
import re

from ..items import YangshengwangItem
from ..spiders.beautifulSoup import processText, processImg
from datetime import datetime
from basespider import BaseTimeCheckSpider

class NewsSpider(scrapy.Spider):

    name = "yanhuang3"
    dict_news = {
     'shicai/shucai':'蔬菜&养生食材',
     'shicai/shuiguo':'水果&养生食材',
     'shicai/roulei':'肉类&养生食材',
     'shicai/shuichan':'水产&养生食材',
     'shicai/yaoshi':'药食&养生食材',
     'shicai/zaliang':' 杂粮&养生食材',
     'shicai/qita':' 其他&养生食材'
    }
    start_urls = ['http://www.yhys.com/%s/' % x for x in dict_news.keys()]

    def parse(self, response):
        next_requests = list()
        #urls = response.xpath('//*[@class="cai700"]/li/a/@href').extract()
        for part_info in response.xpath('//*[@class="shicai_pic"]/li'):
            url = part_info.xpath('a/@href').extract_first()
            req = scrapy.Request(url=url, callback=self.parse_info)

            m_item = YangshengwangItem()
            m_item["classNum"] = 2
            key_word = re.search('com/(.+)/', response.url).group(1)
            total_str = self.dict_news[key_word]
            m_item["className"] = total_str.split('&')[1]
            m_item["specificName"] = total_str.split('&')[0]
            m_item["title"] = part_info.xpath('a/@title').extract_first()
            # 相当于在request中加入了item这个元素
            req.meta['item'] = m_item
            next_requests.append(req)

        for req in next_requests:
            yield req

    def parse_info(self, response):
        item = response.meta['item']
        item["module"] = "健康资讯"
        item["source"] = "炎黄养生网"
        item["sourceUrl"] = response.url
        text_list = response.xpath('//*[@class="wrap1000"]/*[@class="left"]/*')[:-1]
        item["text"] = processText(text_list)
        img_list = response.xpath('//*[@class="boxhead"]/*').extract_first()
        item["imageUrls"] = processImg(img_list)

        yield item
