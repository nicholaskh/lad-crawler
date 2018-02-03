# coding=utf-8
import scrapy
import re

from ..items import VideoItem


class newsSpider(scrapy.Spider):
    name = "xuetaodi"
    start_urls = ['http://www.chuiyue.com/playdata/109/26477.js?50460.09']

    def parse(self, response):
        urls = urls = response.text.split(',')
        vids = []
        del urls[-1]
        del urls[0]
        for each in urls:
            vid = each.split('\\')[-1].split("$")[1]
            url = "http://v.youku.com/v_show/id_" + vid + ".html"
            req = scrapy.Request(url=url, callback=self.parse_youku)
            req.meta['vid'] = vid
            yield req

    def parse_youku(self, response):
        vid = response.meta['vid']
        item = VideoItem()
        item["module"] = "兴趣爱好"
        item['className'] = "学陶笛"
        title = response.xpath('//*[@id="module_basic_title"]/div[1]/h1/@title').extract_first()
        if title is not None:
            item["title"] = title
            item["url"] = "http://player.youku.com/embed/" + vid
            item["source"] = "优酷视频"
            item["sourceUrl"] = "http://v.youku.com/v_show/id_" + vid + ".html"
            item["poster"] = None
            item["edition"] = None
            yield item
