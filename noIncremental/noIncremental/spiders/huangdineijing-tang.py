#coding=utf-8
import scrapy
from ..items import VideoItem
import re

#Code: Tom Tang
class WeChatSpider(scrapy.Spider):
    name = "huangdineijing"
    start_urls = ['https://mp.weixin.qq.com/s?__biz=MzIzMTcyMzY4OA==&mid=2247483727&idx=1&sn=554988df8c85db0f85bffa6c7dfe4245&scene=21#wechat_redirect']

    def parse(self, response):
        urls_ori1 = response.xpath('//*[@id="js_content"]/section[2]//a/@href').extract()
        urls_ori2 = response.xpath('//*[@id="js_content"]/section[4]//a/@href').extract()
        urls_ori3 = response.xpath('//*[@id="js_content"]/section[6]//a/@href').extract()

        url_lists1 = list(set(urls_ori1))
        url_lists2 = list(set(urls_ori2))
        url_lists3 = list(set(urls_ori3))

        for url_next in url_lists1:
            if url_next.split('.')[1] == "youku":
                req = scrapy.Request(url=url_next, callback=self.youku_parseinfo1)
                item = VideoItem()
                item["sourceUrl"] = url_next
                req.meta["m_item"] = item
                yield req

        for url_next in url_lists2:
            if url_next.split('.')[1] == "youku":
                req = scrapy.Request(url=url_next, callback=self.youku_parseinfo2)
                item = VideoItem()
                item["sourceUrl"] = url_next
                req.meta["m_item"] = item
                yield req

        for url_next in url_lists3:
            if url_next.split('.')[1] == "youku":
                req = scrapy.Request(url=url_next, callback=self.youku_parseinfo3)
                item = VideoItem()
                item["sourceUrl"] = url_next
                req.meta["m_item"] = item
                yield req

    def youku_parseinfo1(self, response):
        page_url = response.url
        vid = page_url.split('?')[0].split('/')[-1].split('.')[0].split('_')[-1]
        url = "http://player.youku.com/embed/" + vid
        title = response.xpath('//div[@class="base_info"]/h1/@title').extract()[0]
        item1 = response.meta["m_item"]
        item1["module"] = "养生讲坛"
        item1["title"] = u"黄帝内经医理篇-" + title
        item1["source"] = "优酷视频"
        item1["url"] = url
        item1["poster"] = None
        item1["edition"] = None
        item1["className"] = "黄帝内经"

        yield item1

    def youku_parseinfo2(self, response):
        page_url = response.url
        vid = page_url.split('?')[0].split('/')[-1].split('.')[0].split('_')[-1]
        url = "http://player.youku.com/embed/" + vid
        title = response.xpath('//div[@class="base_info"]/h1/@title').extract()[0]
        item1 = response.meta["m_item"]
        item1["module"] = "养生讲坛"
        item1["title"] = u"黄帝内经医史篇-" + title
        item1["source"] = "优酷视频"
        item1["url"] = url
        item1["poster"] = None
        item1["edition"] = None
        item1["className"] = "黄帝内经"

        yield item1

    def youku_parseinfo3(self, response):
        page_url = response.url
        vid = page_url.split('?')[0].split('/')[-1].split('.')[0].split('_')[-1]
        url = "http://player.youku.com/embed/" + vid
        title = response.xpath('//div[@class="base_info"]/h1/@title').extract()[0]
        item1 = response.meta["m_item"]
        item1["module"] = "养生讲坛"
        item1["title"] = u"黄帝内经养生篇-" + title
        item1["source"] = "优酷视频"
        item1["url"] = url
        item1["poster"] = None
        item1["edition"] = None
        item1["className"] = "黄帝内经"

        yield item1