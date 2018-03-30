#coding=utf-8
import scrapy
from ..items import VideoItem
import requests
import json
import re

#Code: Tom Tang
class WeChatSpider(scrapy.Spider):
    name = "beiwei30du"
    start_urls = ["https://mp.weixin.qq.com/s?__biz=MzIzMTcyMzY4OA==&mid=2247484888&idx=4&sn=9a8bcdf52dc44b14e481f8124729aa16&scene=21#wechat_redirect"]

    def parse(self, response):
        data_ori = response.xpath('//*[@id="js_content"]/section[3]/section/section/section/section/section/section/p').extract()
        for i in range(len(data_ori)):
            url_next = re.findall(r'<a href="(.*?)"',data_ori[i])[0]
            title = re.findall(r'\);">(.*?)</span></strong>',data_ori[i])[0]
            if url_next.split('.')[1] == "cntv":
                if url_next.split('.')[0] == "http://tv":
                    req = scrapy.Request(url=url_next, callback=self.parse_contentid)
                    item = VideoItem()
                    item["sourceUrl"] = url_next
                    item["title"] = title
                    req.meta["m_item"] = item
                    yield req
                elif url_next.split('.')[0] == "http://travel":
                    req = scrapy.Request(url=url_next, callback=self.parse_travelcntv_contentid)
                    item = VideoItem()
                    item["sourceUrl"] = url_next
                    item["title"] = title
                    req.meta["m_item"] = item
                    yield req
            elif url_next.split('.')[1] == "cctv":
                req = scrapy.Request(url=url_next,callback=self.parse_cctv_contentid)
                item = VideoItem()
                item["sourceUrl"] = url_next
                item["title"] = title
                req.meta["m_item"] = item
                yield req

    def parse_contentid(self,response):
        contentid = str(response.xpath('//*[@name="contentid"]/@content').extract()[0])
        url_info = "http://vdn.apps.cntv.cn/api/getHttpVideoInfo.do?pid=" + contentid
        m_item = response.meta["m_item"]
        req = scrapy.Request(url=url_info,callback=self.parse_info)
        req.meta["item1"] = m_item
        yield req

    def parse_travelcntv_contentid(self,response):
        contentid = re.findall(r'"videoCenterId","(.*?)"',response.text)[0]
        url_info = "http://vdn.apps.cntv.cn/api/getHttpVideoInfo.do?pid=" + contentid
        m_item = response.meta["m_item"]
        req = scrapy.Request(url=url_info, callback=self.parse_info)
        req.meta["item1"] = m_item
        yield req

    def parse_cctv_contentid(self,response):
        contentid = re.findall(r'var guid = "(.*?)";',response.text)[0]
        url_info = "http://vdn.apps.cntv.cn/api/getHttpVideoInfo.do?pid=" + contentid
        m_item = response.meta["m_item"]
        req = scrapy.Request(url=url_info, callback=self.parse_info)
        req.meta["item1"] = m_item
        yield req

    def parse_info(self,response):
        item1 = response.meta["item1"]
        item1["module"] = "户外旅游"
        item1["className"] = "北纬30°·中国行"
        item1["source"] = "中国网络电视台 CNTV"
        item1["edition"] = None

        title_ori = re.findall(r'"title":".*?"', response.text)
        title_ori2 = title_ori[0].split(' ')
        title = ""
        for i in range(2,len(title_ori2)):
            title = title + title_ori2[i]

        #item1["title"] = title[:-1]
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