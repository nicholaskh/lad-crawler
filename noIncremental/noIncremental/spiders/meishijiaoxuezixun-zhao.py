# coding=utf-8
import scrapy
import re

from ..items import VideoItem


class newsSpider(scrapy.Spider):
    name = "meishijiaoxuezixun"
    start_urls = ['https://mp.weixin.qq.com/s?__biz=MzIzMTcyMzY4OA==&mid=2247483979&idx=4&sn=1fa9e2f3ffe40c2d2127fdb3e5cc5944&chksm=e89e858cdfe90c9a0e4e1c55aa614f4aac48933fff1c25433c1e0f2a4f23bb1e9f4532b07513&mpshare=1&scene=1&srcid=1202tRLLhxxNAHcOAQLVmoqx&pass_ticket=ETzscQemVtZ6bwgJRRIepwgeWsLJ0TLI%2FbX7bjltdspch27wlrDnxzA5vUivZMG7#rd']

    def parse(self, response):
        titles = response.xpath('//p/span/strong/a/@title').extract()
        hrefs = response.xpath('//p/span/strong/a/@href').extract()
        vids = []

        for each in hrefs:
            vid = re.findall('id_(.*?)==.html', each)[0]
            vids.append(vid)

        for title, vid in zip(titles, vids):
            item = VideoItem()
            item["module"] = "健康食谱"
            item["className"] = "暖暖的味道"
            item["title"] = title
            item["url"] = "http://player.youku.com/embed/" + vid
            item["source"] = "优酷视频"
            item["sourceUrl"] = "http://v.youku.com/v_show/id_" + vid + ".html"
            item["poster"] = None
            item["edition"] = None
            yield item


