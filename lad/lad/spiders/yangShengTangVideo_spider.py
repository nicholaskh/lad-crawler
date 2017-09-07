#coding=utf-8
import scrapy

from lad.items import VideoItem
from lad.spiders.beautifulSoup import processText

class newsSpider(scrapy.Spider):
    name = "yangshengvideo"
    dict_commens = {'2016', '2015', '2014', '2013', '2012', '2017'}
    start_urls = ['http://www.100yangsheng.com/yst%s/' % x for x in dict_commens]
    text = ""

    def parse(self, response):
        if response.xpath('//*[@class="pagelist"]/*[@class="thisclass"]/text()').extract_first() < response.xpath('//*[@class="pageinfo"]/strong/text()').extract_first():
            next_url = response.url.split('list')[0] + response.xpath('//*[@class="pagelist"]/li')[-4].xpath('a/@href').extract_first()
            yield scrapy.Request(url=next_url, callback=self.parse)

        for infoDiv in response.xpath('//*[@class="list-list"]/div/strong/a/@href').extract():
            n_url = infoDiv
            yield scrapy.Request(url=n_url, callback=self.parse_info)

    def parse_info(self, response):
        item = VideoItem()

        item["title"] = response.xpath('//*[@class="body lv"]/h1/text()').extract_first()
        len_time = len(response.xpath('//*[@class="bodyinfo"]/text()').extract_first().split(' ')[0])
        item["time"] = response.xpath('//*[@class="bodyinfo"]/text()').extract_first().split(' ')[0][len_time-10:len_time]
        item["source"] = "百年养生网"
        item["sourceUrl"] = response.url
        item["videoLink"] = response.xpath('//*[@height="500"]/@src').extract_first()
        text_list = response.xpath('//*[@class="body lv"]/*')
        item["text"] = processText(text_list)
        self.text = ""

        yield item
