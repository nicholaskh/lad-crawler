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

    name = "lanren2"
    dict_news = [
 '7890'
 '34740',
 '34739',
 '33618',
 '33614',
 '33281',
 '30549',
 '30548',
 '30535',
 '29583',
 '28479',
 '6389',
 '6264',
 '6083',
 '5979',
 '4497',
 '4490',
 '4489',
 '4466',
 '2125',
 '28799',
 '28798',
 '28256',
 '6320',
 '6023',
 '2448',
 '2446',
 '1641',
 '34742',
 '33615',
 '33482',
 '33294',
 '33282',
 '33280',
 '33279',
 '32673',
 '32672',
 '32319',
 '30547',
 '30540',
 '30538',
 '30537',
 '30534',
 '30533',
 '30530',
 '30360',
 '30359',
 '30326'
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
