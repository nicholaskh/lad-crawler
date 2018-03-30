#coding=utf-8
import scrapy
from ..items import VideoItem
import requests
import json
import re

#Code: Tom Tang
class WeChatSpider(scrapy.Spider):
    name = "changchengneiwai"
    start_urls = ["https://mp.weixin.qq.com/s?__biz=MzIzMTcyMzY4OA==&mid=2247485475&idx=4&sn=378527a079eac718683e29a2340dc8e5&scene=21#wechat_redirect"]

    def parse(self, response):
        urls_ori =  response.xpath('//*[@id="js_content"]/section[4]/section/section/section/section/section/section/ul//a/@href').extract()
        urls = list(set(urls_ori))
        for url_next in urls:
            req = scrapy.Request(url=url_next,callback=self.parse_contentid)
            item = VideoItem()
            item["sourceUrl"] = url_next
            req.meta["m_item"] = item
            yield req

    def parse_contentid(self,response):
        contentid = str(response.xpath('//*[@name="contentid"]/@content').extract()[0])
        url_info = "http://vdn.apps.cntv.cn/api/getHttpVideoInfo.do?pid=" + contentid
        m_item = response.meta["m_item"]

        title_ori = response.xpath('//div[@class="bread"]/a[3]/text()').extract()[0]
        title_s = title_ori.split(' ')
        title = ""
        for i in range(2, len(title_s)):
            title = title + title_s[i]
            title = title + " "
        m_item["title"] = title[0:-1]

        req = scrapy.Request(url=url_info,callback=self.parse_info)
        req.meta["item1"] = m_item
        yield req


    def parse_info(self,response):
        item1 = response.meta["item1"]
        item1["module"] = "户外旅游"
        item1["className"] = "长城内外"
        item1["source"] = "中国网络电视台 CNTV"
        urls = re.findall('jpg","url":"(.*?)"', response.text)
        # 取最后的清晰度
        last_num = 1000
        for i in range(0, urls.__len__())[::-1]:
            num = int(urls[i].split('-')[-1].split('.')[0], 10)
            if num > last_num:
                item1["url"] = urls[i + 1:]
                break
            elif i == 0:
                item1["url"] = urls
                break
            else:
                last_num = num
        item1["poster"] = None
        item1["edition"] = None
        yield item1

