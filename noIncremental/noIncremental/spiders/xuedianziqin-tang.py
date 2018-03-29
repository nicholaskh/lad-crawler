#coding=utf-8
import scrapy
from ..items import VideoItem
import re

#Code: Tom Tang
class WeChatSpider(scrapy.Spider):
    name = "xuedianziqin"
    start_urls = ['https://mp.weixin.qq.com/s?__biz=MzIzMTcyMzY4OA==&mid=2247484055&idx=5&sn=8b6bbfead94c679c8092fd117e7ddbf1&scene=21#wechat_redirect']

    def parse(self, response):
        url_ori = response.xpath('//*[@id="js_content"]/section[2]/section/section/section[2]/section/section/section//a/@href | //*[@id="js_content"]/section[3]/section/section/section[2]/section/section/section//a/@href | //*[@id="js_content"]/section[4]/section/section/section[2]/section/section/section//a/@href').extract()
        url_lists = list(set(url_ori))
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
                        title = title +title_ori[i]

        item1 = response.meta["m_item"]
        item1["module"] = "兴趣爱好"
        item1["title"] = title
        item1["source"] = "腾讯视频"
        item1["url"] = url
        item1["poster"] = None
        item1["edition"] = None
        item1["className"] = "学电子琴"

        yield item1

    def youku_parseinfo(self, response):
        page_url = response.url
        vid = page_url.split('?')[0].split('/')[-1].split('.')[0].split('_')[-1]
        url = "http://player.youku.com/embed/" + vid
        title = response.xpath('//div[@class="base_info"]/h1/@title').extract()[0]
        item1 = response.meta["m_item"]
        item1["module"] = "兴趣爱好"
        item1["title"] = title
        item1["source"] = "优酷视频"
        item1["url"] = url
        item1["poster"] = None
        item1["edition"] = None
        item1["className"] = "学电子琴"

        yield item1