# coding=utf-8
import scrapy
import re

from ..items import VideoItem


class newsSpider(scrapy.Spider):
    name = "shenghuoqiaomen"
    start_urls = ['https://mp.weixin.qq.com/s?__biz=MzIzMTcyMzY4OA==&mid=2247483793&idx=4&sn=8169564a4d4b38aacfb5ef20a41fcdec&scene=21#wechat_redirect']

    def parse(self, response):
        hrefs = response.xpath('//div[@class="rich_media_content "]//a/@href').extract()
        for href in hrefs:
            if "qq.com" in href:
                req = scrapy.Request(url=href, callback=self.parse_tencent)
                yield req
            elif "sohu" in href:
                req = scrapy.Request(url=href, callback=self.parse_sohu)
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
        item["module"] = "户外旅游"
        item['className'] = "生活窍门"
        item["title"] = title
        item["url"] = url
        item["source"] = "腾讯视频"
        item["sourceUrl"] = page_url
        item["poster"] = None
        item["edition"] = None
        yield item

    def parse_sohu(self, response):
        title = response.xpath('//div[@class="area cfix"][1]/div[1]/h1/@title | //div[@class="area cfix"][1]/div[1]/h2/@title').extract_first()
        page_url = response.url
        vid = re.findall('vid="(.*?)";', response.text)[0]
        url = "http://tv.sohu.com/upload/static/share/share_play.html#" + vid
        item = VideoItem()
        item["module"] = "户外旅游"
        item['className'] = "生活窍门"
        item["title"] = title
        item["url"] = url
        item["source"] = "搜狐视频"
        item["sourceUrl"] = page_url
        item["poster"] = None
        item["edition"] = None
        yield item
