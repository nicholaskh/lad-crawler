#coding=utf-8
import scrapy
from ..items import VideoItem
import requests
import json
import re

#Code: Tom Tang
class WeChatSpider(scrapy.Spider):
    name = "xuezuocai"
    start_urls = ["https://mp.weixin.qq.com/s/PTonOTFT_ck2T6lMS7-tpQ"]

    def parse(self, response):
        url_ori = response.xpath('//*[@id="js_content"]/section[4]/section/section/section/section[2]/section/section/section/section/ul//a/@href').extract()
        url_lists = list(set(url_ori))
        for url_next in url_lists:
            req = scrapy.Request(url=url_next,callback=self.parse_contentid)
            item = VideoItem()
            item["sourceUrl"] = url_next
            req.meta["m_item"] = item
            yield req

    def parse_contentid(self,response):
        contentid = str(response.xpath('//*[@name="contentid"]/@content').extract()[0])
        url_info = "http://vdn.apps.cntv.cn/api/getHttpVideoInfo.do?pid=" + contentid
        m_item = response.meta["m_item"]
        req = scrapy.Request(url=url_info,callback=self.parse_info)
        req.meta["item1"] = m_item
        yield req


    def parse_info(self,response):
        item1 = response.meta["item1"]
        item1["module"] = "兴趣爱好"
        item1["className"] = "学做菜"
        item1["source"] = "中国网络电视台 CNTV"

        title_ori = re.findall(r'"title":".*?"', response.text)
        title_ori2 = title_ori[0].split(' ')
        title = ""
        for i in range(2, len(title_ori2)):
            title = title + title_ori2[i]

        if title[0:4] == u"天天饮食":
            item1["title"] = title[4:-1]
        else:
            item1["title"] = title[:-1]

        item1["edition"] = None
        item1["poster"] = None
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

        yield item1