#coding=utf-8
import scrapy
from ..items import VideoItem
import re

#Code: Tom Tang
class WeChatSpider(scrapy.Spider):
    name = "daizhong-zhongyike"
    start_urls = ['http://www.iqiyi.com/a_19rrh0f1p1.html']

    def parse(self, response):
        url_ori = response.xpath('//*[@id="albumpic-showall-wrap"]//a/@href').extract()
        url_lists = list(set(url_ori))
        for url_next in url_lists:
            req = scrapy.Request(url=url_next, callback=self.iqiyi_parseinfo)
            item = VideoItem()
            item["sourceUrl"] = url_next
            req.meta["m_item"] = item
            yield req

    def iqiyi_parseinfo(self, response):
        vid = str(re.findall(r'data-player-videoid="(.*?)"', response.text)[0])
        tvld = str(re.findall(r'tvId:(.*?),',response.text)[0])
        url = "http://open.iqiyi.com/developer/player_js/coopPlayerIndex.html?vid=" + vid + "&tvId=" + tvld
        title = response.xpath('//*[@id="widget-videotitle"]/text()').extract()[0][1:]

        item1 = response.meta["m_item"]
        item1["module"] = "名医讲座"
        item1["className"] = "戴中—中医科"
        item1["title"] = title
        item1["source"] = "爱奇艺"
        item1["url"] = url
        item1["edition"] = None
        item1["poster"] = None

        yield item1