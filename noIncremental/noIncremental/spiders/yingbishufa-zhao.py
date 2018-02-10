# coding=utf-8
import scrapy
import re

from ..items import VideoItem


class newsSpider(scrapy.Spider):
    name = "yingbishufa"
    start_urls = ['http://www.iqiyi.com/v_19rr9qodb4.html',
                  'http://www.iqiyi.com/v_19rraj4474.html',
                  'http://www.iqiyi.com/v_19rr7l0y5w.html']

    def parse(self, response):
        lis = response.xpath('//div[@data-tab-page="body"]//li')
        for li in lis:
            title = li.xpath('a/@title').extract_first()
            source_url = li.xpath('a/@href').extract_first()
            tvid = li.xpath('@data-videolist-tvid').extract_first()
            vid = li.xpath('@data-videolist-vid').extract_first()
            url = "http://open.iqiyi.com/developer/player_js/coopPlayerIndex.html?vid=" + vid + \
                  "&tvId=" + tvid
            item = VideoItem()
            item["module"] = "兴趣爱好"
            item['className'] = "硬笔书法"
            item["title"] = title
            item["url"] = url
            item["source"] = "爱奇艺"
            item["sourceUrl"] = "http:" + source_url
            item["poster"] = None
            item["edition"] = None
            yield item
