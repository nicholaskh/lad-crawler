#coding=utf-8
import scrapy
from ..items import VideoItem
import re

#Code: Tom Tang
class WeChatSpider(scrapy.Spider):
    name = "lishuangjiang"
    start_urls = ['https://mp.weixin.qq.com/s?__biz=MzIzMTcyMzY4OA==&mid=2247484055&idx=3&sn=a1c7b9a2d7190ef4f9b1145a32f62d00&chksm=e89e8550dfe90c46b9f051cb1079f652cdd044fb5b366271c6d3641d538ec81c023ae95cae2a&mpshare=1&scene=1&srcid=1202X5BOUQfunvQhtpVxfdyJ&pass_ticket=ETzscQemVtZ6bwgJRRIepwgeWsLJ0TLI%2FbX7bjltdspch27wlrDnxzA5vUivZMG7#rd']

    def parse(self, response):
        url_lists = response.xpath('//*[@id="js_content"]//a/@href').extract()
        for url_next in url_lists:
            if url_next.split('.')[1] == "youku":
                req = scrapy.Request(url=url_next, callback=self.youku_parseinfo)
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
        item1["module"] = "歌唱家"
        item1["title"] = title
        item1["source"] = "腾讯视频"
        item1["url"] = url
        item1["edition"] = None
        item1["poster"] = None

        if title[0]== u"阎":
            item1["className"] = "阎维文"
        elif u"黄" in title:
            item1["className"] = "黄华丽"
        elif u"马" in title:
            item1["className"] = "马秋华"
        elif u"王宏伟" in title:
            item1["className"] = "王宏伟"
        else:
            item1["className"] = "教您学唱歌"

        yield item1

    def youku_parseinfo(self, response):
        page_url = response.url
        vid = page_url.split('?')[0].split('/')[-1].split('.')[0].split('_')[-1]
        url = "http://player.youku.com/embed/" + vid
        title = response.xpath('//div[@class="base_info"]/h1/@title').extract()[0]
        item1 = response.meta["m_item"]
        item1["module"] = "歌唱家"
        item1["title"] = title
        item1["source"] = "优酷视频"
        item1["url"] = url
        item1["edition"] = None
        item1["poster"] = None
        item1["className"] = "戴玉强"

        yield item1
