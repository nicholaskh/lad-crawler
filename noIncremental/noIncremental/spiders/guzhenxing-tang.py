#coding=utf-8
import scrapy
from ..items import VideoItem
import requests
import json
import re

#Code: Tom Tang
class WeChatSpider(scrapy.Spider):
    name = "guzhenxing"
    start_urls = ["https://mp.weixin.qq.com/s?__biz=MzIzMTcyMzY4OA==&mid=2247483847&idx=2&sn=33f89ef73f8119727063444df35661c9&scene=21#wechat_redirect"]

    def parse(self, response):
        url_ori = response.xpath('//*[@id="js_content"]/section[2]//a/@href | //*[@id="js_content"]/section[3]//a/@href').extract()
        url_lists = list(set(url_ori))
        for url_next in url_lists:
            if url_next.split('.')[1] == "cntv":
                req = scrapy.Request(url=url_next, callback=self.parse_contentid)
                item = VideoItem()
                item["sourceUrl"] = url_next
                req.meta["m_item"] = item
                yield req
            elif url_next.split('.')[1] == "cctv":
                req = scrapy.Request(url=url_next,callback=self.parse_cctv_contentid)
                item = VideoItem()
                item["sourceUrl"] = url_next
                req.meta["m_item"] = item
                yield req
            elif url_next.split('.')[1] == "youku":
                req = scrapy.Request(url=url_next,callback=self.youku_parseinfo)
                item = VideoItem()
                item["sourceUrl"] = url_next
                req.meta["m_item"] = item
                yield req

    def youku_parseinfo(self, response):
        page_url = response.url
        vid = page_url.split('?')[0].split('/')[-1].split('.')[0].split('_')[-1]
        url = "http://player.youku.com/embed/" + vid
        title = response.xpath('//div[@class="base_info"]/h1/@title').extract()[0]
        item1 = response.meta["m_item"]
        item1["module"] = "户外旅游"
        item1["title"] = title
        item1["source"] = "优酷视频"
        item1["url"] = url
        item1["poster"] = None
        item1["edition"] = None
        item1["className"] = "古镇行"
        yield item1

    def parse_contentid(self,response):
        contentid = str(response.xpath('//*[@name="contentid"]/@content').extract()[0])
        url_info = "http://vdn.apps.cntv.cn/api/getHttpVideoInfo.do?pid=" + contentid
        m_item = response.meta["m_item"]
        req = scrapy.Request(url=url_info,callback=self.parse_info)
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
        item1["className"] = "古镇行"
        item1["source"] = "中国网络电视台 CNTV"
        item1["edition"] = None

        title_ori = re.findall(r'"title":".*?"', response.text)
        title_ori2 = title_ori[0].split(' ')
        title = ""
        for i in range(2,len(title_ori2)):
            title = title + title_ori2[i]

        if title[0:9] == u"[走遍中国]中国古镇":
            item1["title"] = title[9:-1]
        else:
            item1["title"] = title[:-1]

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