#coding=utf-8
import scrapy
from ..items import VideoItem
import re

#Code: Tom Tang
class WeChatSpider(scrapy.Spider):
    name = 'iqiyi-4'
    start_dicts = {'http://www.iqiyi.com/a_19rrh93sx5.html':'法治进行时'}
    start_urls = list(start_dicts.keys())

    def parse(self, response):
        sourceId = re.findall(r'sourceId: (.*?),', response.text)[0]
        categoryId = response.xpath('//div[@style="display: none;"]/div/@data-qitancomment-categoryid').extract()[0]
        dataUrl = 'http://cache.video.iqiyi.com/jp/sdvlst/' + categoryId + '/' + sourceId + '/'
        if sourceId == '0':
            albumId = re.findall(r'albumId: (.*?),', response.text)[0]
            dataUrl = 'http://cache.video.iqiyi.com/jp/avlist/' + albumId + '/'
        req = scrapy.Request(url=dataUrl, callback=self.iqiyi_parseDataInfo)
        item = VideoItem()
        item["module"] = "教育法律"
        item["className"] = self.start_dicts[response.url]
        req.meta["mm_item"] = item
        yield req

    def iqiyi_parseDataInfo(self, response):
        if 'sdvlst' in response.url:
            urls = re.findall(r'"vUrl":"(.*?)"', response.text)
        elif 'avlist' in response.url:
            urls = re.findall(r'"vurl":"(.*?)"', response.text)
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