#coding=utf-8
import scrapy
import re
from ..items import VideoItem

#Code: Tom Tang
class WeChatSpider(scrapy.Spider):
    name = "woaimantangcai"
    start_urls = ['https://mp.weixin.qq.com/s?__biz=MzIzMTcyMzY4OA==&mid=2247486459&idx=6&sn=595dc486f266d892ec72f3fb8f8b9e23&chksm=e89e8c3cdfe9052ac3251fac77879b366b36a2e85e42f0ef572dc9cab4be2de52638cf0fb83a&mpshare=1&scene=1&srcid=1202ZUmAxwArej5DMZNIKhkg&pass_ticket=ETzscQemVtZ6bwgJRRIepwgeWsLJ0TLI%2FbX7bjltdspch27wlrDnxzA5vUivZMG7#rd']

    def parse(self, response):
        url_lists_ori = response.xpath('//*[@style="text-align: left;line-height: 2em;"]//a/@href | //*[@style="text-align: left;"]//a/@href').extract()
        url_lists = list(set(url_lists_ori))
        for url_next in url_lists:
            req = scrapy.Request(url=url_next, callback=self.parse_contentid)
            item = VideoItem()
            item["sourceUrl"] = url_next
            req.meta["m_item"] = item
            yield req

    def parse_contentid(self, response):
        contentid = str(response.xpath('//*[@name="contentid"]/@content').extract()[0])
        url_info = "http://vdn.apps.cntv.cn/api/getHttpVideoInfo.do?pid=" + contentid
        m_item = response.meta["m_item"]
        req = scrapy.Request(url=url_info, callback=self.parse_info)
        req.meta["item1"] = m_item
        yield req

    def parse_info(self, response):
        item1 = response.meta["item1"]
        item1["module"] = "节目展演"
        item1["className"] = "我爱满堂彩"
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