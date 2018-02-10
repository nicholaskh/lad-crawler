# coding=utf-8
import scrapy
import re

from ..items import VideoItem


class newsSpider(scrapy.Spider):
    name = "wudaoheji"
    start_urls = ['https://mp.weixin.qq.com/s?__biz=MzIzMTcyMzY4OA==&mid=2247485475&idx=3&sn=0ea3504c6ad9255813ef76ec8f351cc5&chksm=e89e8fe4dfe906f21fb0a14a403eb314c640638aea5843331e156e4d0aa6b57a6be811c01831&scene=21#wechat_redirect']

    def parse(self, response):
        urls = response.xpath('//section[@style="background-color: rgb(255, 255, 255); box-sizing: border-box;"]//a/@href').extract()
        for url in urls:
            req = scrapy.Request(url=url, callback=self.parse_vid)
            yield req

    def parse_vid(self, response):
        url = response.xpath('//iframe[@class="video_iframe"]/@data-src').extract_first()
        if url is not None:
            vid = url.split('&')[0].split('=')[-1]
            source_url = "https://v.qq.com/x/page/" + vid + ".html"
            req = scrapy.Request(url=source_url, callback=self.parse_tencent)
            yield req

    def parse_tencent(self, response):
        page_url = response.url
        vid = page_url.split('/')[-1].split('.')[0]
        url = "https://v.qq.com/iframe/player.html?vid=" + vid + "&tiny=0&auto=0"
        title_ori = response.xpath('//div[@class="mod_intro"]/div/h1/text()').extract()[0]
        title = ""
        for i in range(len(title_ori)):
            if title_ori[i] != '\n':
                if title_ori[i] != ' ':
                    if title_ori[i] != '\t':
                        title = title + title_ori[i]
        item = VideoItem()
        item["module"] = "节目展演"
        item['className'] = "舞蹈合集"
        item["title"] = title
        item["url"] = url
        item["source"] = "腾讯视频"
        item["sourceUrl"] = page_url
        item["poster"] = None
        item["edition"] = None
        yield item
