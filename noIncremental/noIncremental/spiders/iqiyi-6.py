#coding=utf-8
import scrapy
from ..items import VideoItem
import re

#Code: Tom Tang
class WeChatSpider(scrapy.Spider):
    name = "iqiyi-6"
    start_dicts = {'http://www.iqiyi.com/playlist446880102.html': '健康食谱',
                   'http://www.iqiyi.com/playlist409180602.html': '宝宝健康营养食谱',
                   'http://www.iqiyi.com/playlist414235802.html': '补气血粥',
                   'http://www.iqiyi.com/playlist412415802.html': '养生美食',
                   'http://www.iqiyi.com/playlist270294002.html': '健康搭配每日菜谱',
                   'http://www.iqiyi.com/playlist402999202.html': '健康长寿幸福食谱',
                   'http://www.iqiyi.com/playlist489723902.html': '健康饮品菜谱'}
    start_urls = list(start_dicts.keys())

    def parse(self, response):
        urls = response.xpath('//div[@class="piclist-wrapper"]/ul//li/div/a/@href').extract()
        for url_next in urls:
            req = scrapy.Request(url=url_next, callback=self.iqiyi_parseinfo)
            item = VideoItem()
            item["module"] = "健康食谱"
            item["className"] = self.start_dicts[response.url]
            req.meta["m_item"] = item
            yield req

    def iqiyi_parseinfo(self, response):
        vid = str(re.findall(r'data-player-videoid="(.*?)"', response.text)[0])
        tvld = str(re.findall(r'tvId:(.*?),',response.text)[0])[1:]
        url = "http://open.iqiyi.com/developer/player_js/coopPlayerIndex.html?vid=" + vid + "&tvId=" + tvld
        title = response.xpath('//*[@id="widget-videoname"]/text()').extract()[0]

        item1 = response.meta["m_item"]
        item1["title"] = title
        item1["source"] = "爱奇艺"
        item1["sourceUrl"] = response.url
        item1["url"] = url
        item1["edition"] = None
        item1["poster"] = None

        yield item1