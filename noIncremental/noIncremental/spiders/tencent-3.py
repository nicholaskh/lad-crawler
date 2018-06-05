#coding=utf-8
import scrapy
from ..items import VideoItem
import re

#Code: Tom Tang
class WeChatSpider(scrapy.Spider):
    name = 'tencent-3'
    start_dicts = {'http://v.qq.com/detail/s/sdp001tooxv5p6y.html':'宝宝健康食谱原创',
                   'http://v.qq.com/detail/s/sdp001grxfmlgw2.html':'湘菜美食食谱',
                   'http://v.qq.com/detail/s/sdp001sexcjp8z9.html':'营养早餐做法',
                   'http://v.qq.com/detail/s/sdp001qz25sg3rz.html':'川菜食谱'}
    start_urls = list(start_dicts.keys())

    def parse(self, response):
        id = response.url.split('/')[-1].split('.')[0]
        month = 6
        while month > 1:
            month = month -1
            dataUrl = 'http://s.video.qq.com/get_playsource?id=' + id + '&type=4&year=2018&month=' + str(month) + '&otype=json'
            req = scrapy.Request(url=dataUrl, callback=self.tencent_parseDataInfo)
            item = VideoItem()
            item["module"] = "健康食谱"
            item["className"] = self.start_dicts[response.url]
            req.meta["mm_item"] = item
            yield req

    def tencent_parseDataInfo(self, response):
        urls = re.findall(r'"playUrl":"(.*?)"',response.text)
        for eachUrl in urls:
            item11 = response.meta["mm_item"]
            req = scrapy.Request(eachUrl, callback=self.iqiyi_parseinfo)
            req.meta["m_item"] = item11
            yield req

    def iqiyi_parseinfo(self, response):
        vid = str(re.findall(r'data-player-videoid="(.*?)"', response.text)[0])
        tvld = str(re.findall(r'tvId:(.*?),',response.text)[0])
        url = "http://open.iqiyi.com/developer/player_js/coopPlayerIndex.html?vid=" + vid + "&tvId=" + tvld
        title = response.xpath('//*[@id="widget-videotitle"]/text()').extract()[0][1:]

        item1 = response.meta["m_item"]
        item1["title"] = title
        item1["source"] = "爱奇艺"
        item1["sourceUrl"] = response.url
        item1["url"] = url
        item1["edition"] = None
        item1["poster"] = None

        yield item1