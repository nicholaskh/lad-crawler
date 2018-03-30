#coding=utf-8
import scrapy
from ..items import VideoItem
import requests
import json
import re

#Code: Tom Tang
class WeChatSpider(scrapy.Spider):
    name = "meilixiangcunzhongguoxing"
    start_urls = ["https://mp.weixin.qq.com/s?__biz=MzIzMTcyMzY4OA==&mid=2247487704&idx=4&sn=1c9178db74695829098c579c478548ce&chksm=e89e971fdfe91e096c1eda5570cfdc9e4252f69b26044728404ce6191ed243d54c63ff79a4e4&mpshare=1&scene=1&srcid=1202fGQk7n1iYBZqSYm50Ocg&pass_ticket=ETzscQemVtZ6bwgJRRIepwgeWsLJ0TLI%2FbX7bjltdspch27wlrDnxzA5vUivZMG7#rd"]

    def parse(self, response):
        url_lists = response.xpath('//*[@style="box-sizing: border-box;"]/ul/p/a/@href | //*[@style="box-sizing: border-box;"]/ul/li/p/a/@href').extract()
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
        item1["className"] = "乡村游"
        item1["source"] = "中国网络电视台 CNTV"
        title_ori = re.findall(r'"title":".*?"', response.text)
        item1["edition"] = None
        item1["title"] = title_ori[0].split(' ')[2].split('"')[0]
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