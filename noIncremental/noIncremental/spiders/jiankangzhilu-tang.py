#coding=utf-8
import scrapy
from ..items import VideoItem
import requests
import json
import re
import random

#Code: Tom Tang
class WeChatSpider(scrapy.Spider):
    name = "jiankangzhilu"
    start_urls = ["http://mp.weixin.qq.com/s?__biz=MzIzMTcyMzY4OA==&mid=2247483979&idx=1&sn=639bb32e390af6acacb2bdfa173c5489&chksm=e89e858cdfe90c9a83f150fb1d47df07a6141c3c22eb6a68bd5b587d9759ef9961e2e1ab8b12&mpshare=1&scene=1&srcid=1202fa3PCyu7DeKvD6hPhVmh#rd"]

    def parse(self, response):
        url_lists = response.xpath('//*[@style="box-sizing: border-box;"]/p/a/@href').extract()
        for url_next in url_lists:
            req = scrapy.Request(url=url_next,callback=self.parse_contentid)
            item = VideoItem()
            item["sourceUrl"] = url_next
            req.meta["m_item"] = item
            yield req

    def parse_contentid(self,response):
        contentid = str(response.xpath('//*[@name="contentid"]/@content').extract()[0])
        url_info = "http://vdn.apps.cntv.cn/api/getHttpVideoInfo.do?pid=" + contentid + "&tz=-8&from=000tv&url=http://tv.cntv.cn/video/C10606/29f3cd18ba02492b89385ee1a91736ad&idl=32&idlr=32&modifyed=false"
        m_item = response.meta["m_item"]
        req = scrapy.Request(url=url_info,callback=self.parse_info)
        req.meta["item1"] = m_item
        yield req


    def parse_info(self,response):
        item1 = response.meta["item1"]
        item1["module"] = "养生讲坛"
        item1["className"] = "健康之路"
        item1["source"] = "中国网络电视台 CNTV"
        title_ori = re.findall(r'"title":".*?"', response.text)
        item1["edition"] = None
        item1["title"] = title_ori[0].split(' ')[2].split('"')[0]
        item1["poster"] = None
        item1["edition"] = None
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