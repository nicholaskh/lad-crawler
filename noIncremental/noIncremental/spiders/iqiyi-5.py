#coding=utf-8
import scrapy
from ..items import VideoItem
import re

#Code: Tom Tang
class WeChatSpider(scrapy.Spider):
    name = "iqiyi-5"
    start_dicts = {'http://www.iqiyi.com/playlist487064502.html': '教师舞蹈',
                   'http://www.iqiyi.com/playlist294880202.html': '经络养生健美操',
                   'http://www.iqiyi.com/playlist282830902.html': '太极功夫扇',
                   'http://www.iqiyi.com/playlist406381402.html': '养生瑜伽',
                   'http://www.iqiyi.com/playlist402740302.html': '养生舞'}
    start_urls = list(start_dicts.keys())

    def parse(self, response):
        urls = response.xpath('//div[@class="piclist-wrapper"]/ul//li/div/a/@href').extract()
        for url_next in urls:
            req = scrapy.Request(url=url_next, callback=self.iqiyi_parseinfo)
            item = VideoItem()
            item["module"] = "舞蹈"
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