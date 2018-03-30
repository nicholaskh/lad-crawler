#coding=utf-8
import scrapy
from ..items import VideoItem
import re

#Code: Tom Tang
class WeChatSpider(scrapy.Spider):
    name = "linianchunwanhui"
    start_urls = ['https://mp.weixin.qq.com/s?__biz=MzIzMTcyMzY4OA==&mid=2247483847&idx=3&sn=111761f0eb9f43141acfd17776b0f5fc&scene=21#wechat_redirect']

    def parse(self, response):
        url_ori = response.xpath('//*[@id="js_content"]/section/section[2]/section/section/section/section/section/section//a/@href').extract()
        url_lists = list(set(url_ori))
        for url_next in url_lists:
            if url_next.split('.')[1] == "iqiyi":
                req = scrapy.Request(url=url_next, callback=self.iqiyi_parseinfo)
                item = VideoItem()
                item["sourceUrl"] = url_next
                req.meta["m_item"] = item
                yield req
            elif url_next.split('.')[1] == "qq":
                req = scrapy.Request(url=url_next, callback=self.tencent_parseinfo)
                item = VideoItem()
                item["sourceUrl"] = url_next
                req.meta["m_item"] = item
                yield req

    def tencent_parseinfo(self, response):
        page_url = response.url
        vid = page_url.split('/')[-1].split('.')[0]
        url = "https://v.qq.com/iframe/player.html?vid=" + vid + "&tiny=0&auto=0"
        title_ori = response.xpath('//div[@class="mod_intro"]/div/h1/text()').extract()[0]
        title = ""
        for i in range(len(title_ori)):
            if title_ori[i] != '\n':
                if title_ori[i] != ' ':
                    if title_ori[i] != '\t':
                        title = title + title_ori[i]

        item1 = response.meta["m_item"]
        item1["module"] = "节目展演"
        item1["className"] = "历年春晚汇"
        item1["title"] = title
        item1["source"] = "腾讯视频"
        item1["url"] = url
        item1["edition"] = None
        item1["poster"] = None

        yield item1

    def iqiyi_parseinfo(self, response):
        vid = str(re.findall(r'data-player-videoid="(.*?)"', response.text)[0])
        tvld = str(re.findall(r'tvId:(.*?),',response.text)[0])
        url = "http://open.iqiyi.com/developer/player_js/coopPlayerIndex.html?vid=" + vid + "&tvId=" + tvld
        title = response.xpath('//*[@id="widget-videotitle"]/text()').extract()[0][1:]

        item1 = response.meta["m_item"]
        item1["module"] = "节目展演"
        item1["className"] = "历年春晚汇"
        item1["title"] = title
        item1["source"] = "爱奇艺"
        item1["url"] = url
        item1["edition"] = None
        item1["poster"] = None

        yield item1