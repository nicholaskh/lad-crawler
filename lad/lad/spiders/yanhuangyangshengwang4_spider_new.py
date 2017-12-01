#coding=utf-8
import scrapy
import re

from ..items import YangshengwangItem
from ..spiders.beautifulSoup import processText, processImg
from datetime import datetime
from basespider import BaseTimeCheckSpider

class NewsSpider(scrapy.Spider):

    name = "yanhuang4"
    dict_news = {
     'jijie/jieqi':'节气养生&四季保健',
     'jijie/yuefen':'月份养生&四季保健',
     'jijie/shichen':'节气养生&四季保健'
    }
    start_urls = ['http://www.yhys.com/%s/' % x for x in dict_news.keys()]

    def parse(self, response):
        next_requests = list()
        #urls = response.xpath('//*[@class="cai700"]/li/a/@href').extract()
        for part_info in response.xpath('//*[@class=" jijie_list_list1"]/ul/li'):
            url = part_info.xpath('a/@href').extract_first()
            req = scrapy.Request(url=url, callback=self.parse_info)

            m_item = YangshengwangItem()
            m_item["classNum"] = 2
            key_word = re.search('com/(.+)/', response.url).group(1)
            total_str = self.dict_news[key_word]
            m_item["className"] = total_str.split('&')[1]
            m_item["specificName"] = total_str.split('&')[0]
            # 相当于在request中加入了item这个元素
            req.meta['item'] = m_item
            next_requests.append(req)

        for req in next_requests:
            yield req

    def parse_info(self, response):
        item = response.meta['item']
        item["title"] = response.xpath('//*[@class="con_left"]/h1/text()').extract_first()
        item["module"] = "健康资讯"
        item["source"] = "炎黄养生网"
        item["sourceUrl"] = response.url
        item["time"] = response.xpath('//*[@class="Information"]/span')[1].xpath('text()').extract_first().encode('utf-8')[9:19]
        text_list = response.xpath('//*[@class="main"]/*')
        item["text"] = processText(text_list)
        img_list = response.xpath('//*[@class="main"]/*').extract()
        item["imageUrls"] = processImgSep(img_list)

        yield item
