#coding=utf-8
import scrapy

from ..items import BroadcastItem
from scrapy.conf import settings
from noIncremental.spiders.beautifulSoup import processText
import requests
import json
import math
import re
import random

class NewsSpider(scrapy.Spider):

    name = "lanren"
    dict_news = [
 '30312',
 '30311',
 '30048',
 '30039',
 '28858',
 '7759',
 '6262',
 '4413',
 '4087',
 '2453',
 '2447',
 '2121',
 '2119',
 '1645',
 '1644',
 '1636',
 '65',
 '31521',
 '30536',
 '30347',
 '30346',
 '30345',
 '30344',
 '30343',
 '30342',
 '30341',
 '30340',
 '30339',
 '30338',
 '30337',
 '30336',
 '30335',
 '30334',
 '30333',
 '30332',
 '30331',
 '30330',
 '30329',
 '30328',
 '30327',
 '30325',
 '30324',
 '30323',
 '30322',
 '30321',
 '30320',
 '30319',
 '30317',
 '30300',
 '6457',
 '6263',
 '6261',
 '2122',
 '1646',
 '1639',
 '5211',
 '4493',
 '2126',
 '7434',
 '6082',
 '4496',
 '2123',
 '2120'
]
    start_urls = ['http://www.lrts.me/book/%s' % x for x in dict_news]

    def parse(self, response):
        next_requests = list()
        total_num = response.xpath('//*[@class="d-r"]/*[@class="d-grid"]/li/text()').extract()[1]
        final_num = math.ceil((float(total_num)) / 10)
        infoDiv = response.xpath('//*[@id="pul"]/li')[0]
        info = infoDiv.xpath('a/@player-info')[-1].extract()
        type_num = info.split('&')[0].split('=')[1]
        resourcesid = info.split('&')[1].split('=')[1]
        for i in range(1,int(final_num)+1):
            num = (i-1)*10+1
            n_url = 'http://www.lrts.me/ajax/playlist/' + type_num + '/' + resourcesid + '/' + str(num)
            item = BroadcastItem()
            item["module"] = response.xpath('//*[@class="d-grid"]/li/text()').extract_first()
            item["className"] = response.xpath('//*[@class="nowrap"]/text()').extract_first()
            item["intro"] = response.xpath('//*[@class="d-desc f14"]/p/text()').extract_first()
            # item["play_times"] = response.xpath('//*[@class="d-p player-trigger "]/span/em/text()').extract_first().strip()
            item["source"] = "懒人听书官网"
            req = scrapy.Request(url=n_url, callback=self.parse_info)
            req.meta['item'] = item
            next_requests.append(req)
        for req in next_requests:
            yield req

    def parse_info(self, response):
        for infoDiv in response.xpath('//*[@class="section"]/li'):
            item = response.meta['item']
            item["title"] = infoDiv.xpath('div/span/text()').extract_first()
            try:
                item["edition"] = re.findall(r"\d+\d*",infoDiv.xpath('div/span/text()').extract_first())[0]
            except:
                print "no edition"
                item["edition"] = None
            item["sourceUrl"] = response.url
            item["broadcast_url"] = infoDiv.xpath('div/input')[0].xpath('@value').extract_first()

            yield item
