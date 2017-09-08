#coding=utf-8
import scrapy

from lad.items import VideoItem
from lad.spiders.beautifulSoup import processText
import re

class newsSpider(scrapy.Spider):
    name = "baishanxi"
    dict_commens = {'yangshengjiemu/zhong-hua', 'yangshengjiemu/shenghuo', 'jiankangzhilu', 'tiantianyangsheng', 'yinshiyangshenghui', 'jujiankang', 'yangshengjiemu/neijing'}
    start_urls = ['http://www.baishanxi.com/%s/' % x for x in dict_commens]
    text = ""

    def parse(self, response):
        if response.xpath('//*[@class="thisclass"]/text()').extract_first() < response.xpath('//*[@class="pageinfo"]/strong/text()').extract_first():
            next_url = response.url.split('list')[0] + response.xpath('//*[@class="pagelist"]/li')[-4].xpath('a/@href').extract_first()
            yield scrapy.Request(url=next_url, callback=self.parse)

        for infoDiv in response.xpath('//*[@class="clearfix"]/li/a/@href').extract():
            n_url = 'http://www.baishanxi.com' + infoDiv
            yield scrapy.Request(url=n_url, callback=self.parse_info)

    def parse_info(self, response):
        item = VideoItem()

        item["title"] = response.xpath('//*[@class="viewbox"]/h1/text()').extract_first()
        s = item["title"]
        m = re.findall(r'(\w*[0-9]+)\w*',s)[0]
        item["time"] = m[0:4] + '-' + m[4:6] + '-' + m[6:8]
        item["source"] = "百山夕养生网"
        item["sourceUrl"] = response.url
        item["videoLink"] = response.xpath('//*[@width="600"]/@src').extract_first()
        text_list = response.xpath('//*[@class="content"]/*')
        item["text"] = processText(text_list)
        self.text = ""

        yield item
