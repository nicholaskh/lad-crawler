#coding=utf-8
import scrapy
from ..items import VideoItem
import re

#Code: Tom Tang
class WeChatSpider(scrapy.Spider):
    name = "tuanshanwu"
    start_urls = ['https://mp.weixin.qq.com/s/5RU8qoSuklHMNitP9ZW02A']

    def parse(self, response):
        urls_ori = response.xpath('//*[@id="js_content"]/section[2]//a/@href').extract()
        url_lists = list(set(urls_ori))
        for url_next in url_lists:
            req = scrapy.Request(url=url_next, callback=self.parse_info)
            yield req

    def parse_info(self, response):
        title_ori = response.xpath('//*[@id="activity-name"]/text()').extract()[0]
        title = ""
        for i in range(len(title_ori)):
            if title_ori[i] != '\n':
                if title_ori[i] != ' ':
                    if title_ori[i] != '\t':
                        title = title +title_ori[i]

        item1 = VideoItem()
        item1["sourceUrl"] = response.url
        item1["module"] = "兴趣爱好"
        item1["title"] = title
        item1["source"] = "优酷视频"
        item1["url"] = response.xpath('//iframe/@data-src').extract()[0]
        item1["poster"] = None
        item1["edition"] = None
        item1["className"] = "团扇舞"

        yield item1