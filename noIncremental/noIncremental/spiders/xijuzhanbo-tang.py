#coding=utf-8
import scrapy
from ..items import VideoItem
import requests
import json
import re

#Code: Tom Tang
class WeChatSpider(scrapy.Spider):
    name = "xijuzhanbo"
    start_urls = ["https://mp.weixin.qq.com/s?__biz=MzIzMTcyMzY4OA==&mid=2247487763&idx=5&sn=4687e16ec3a6f7be1b33baf18d3f1bcf&chksm=e89e96d4dfe91fc268931e0ea4e1edaa824e99f74129732e0938c2cd28ea7d9750dbf703cf07&mpshare=1&scene=1&srcid=0207fDnHI8PBLsUDLgK3NY6z&pass_ticket=X8hh%2BMszHop5erYieQ5sy2NnGUGla5ehPpR0QWm10V7j9q%2F6jjdgWbNe0pztUhJZ#rd"]

    def parse(self, response):
        urls_ori = response.xpath('//*[@id="js_content"]/ul//a/@href | //*[@id="js_content"]/section[5]/section/section/section/section/section/section/section/section/section/section/section/section/section/section/section/section/section/section/section/section/section/section/section/section/section/section/section/section/section/ul//a/@href').extract()
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
        if u"九州大戏台" in title_ori:
            m_item["className"] = "九州大戏台"
        elif u"CCTV空中剧院" in title_ori:
            m_item["className"] = "CCTV空中剧院"
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
        item1["module"] = "节目展演"
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

