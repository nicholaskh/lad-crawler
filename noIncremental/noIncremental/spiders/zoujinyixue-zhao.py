# coding=utf-8
import scrapy
import re

from ..items import VideoItem


class newsSpider(scrapy.Spider):
    name = "zoujinyixue"
    start_urls = ['https://mp.weixin.qq.com/s/k7vEZXXEiXN6Xv0LwnrnBQ']

    def parse(self, response):
        hrefs = response.xpath('//section[@style="box-sizing: border-box;background-color: rgb(255, 255, 255);"]//a/@href').extract()
        for href in hrefs:
            req = scrapy.Request(url=href, callback=self.parse_56)
            req.meta['edition'] = hrefs.index(href) + 1
            yield req

    def parse_56(self, response):
        vid = re.findall('vid: "(.*?)"', response.text)[0]
        pid = re.findall('pid: "(.*?)"', response.text)[0]
        cid = re.findall("cid: '(.*?)'", response.text)[0]
        item = VideoItem()
        item["module"] = "养生讲坛"
        item['className'] = "走进医学"
        title = response.xpath('//div[@class="play_info"]/div/div/h1/@title').extract_first()
        if title is not None:
            item["title"] = title
            item["url"] = "http://tv.sohu.com/upload/static/share/share_play.html#" + vid + "_" + pid + "_0_" + cid
            item["source"] = "56视频"
            item["sourceUrl"] = response.url
            item["poster"] = None
            item["edition"] = response.meta['edition']
            yield item
