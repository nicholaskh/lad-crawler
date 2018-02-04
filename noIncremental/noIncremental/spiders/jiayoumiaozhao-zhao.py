# coding=utf-8
import scrapy
import re

from ..items import VideoItem


class newsSpider(scrapy.Spider):
    name = "jiayoumiaozhao"
    start_urls = ['https://mp.weixin.qq.com/s?__biz=MzIzMTcyMzY4OA==&mid=2247483885&idx=3&sn=acb6c94e2bddbcd5670665d590b51f7b&scene=21#wechat_redirect']

    def parse(self, response):
        alabels = response.xpath('//section[@style="padding-top: 3.5em; padding-bottom: 15px; text-align: left; box-sizing: border-box;"]/p/a')
        for alabel in alabels:
            title = alabel.xpath('strong/text()').extract_first()
            url = alabel.xpath('@href').extract_first()
            if title is not None and "youku" in url:
                item = VideoItem()
                item["module"] = "户外旅游"
                item['className'] = "家有妙招"
                item["title"] = title
                vid = re.findall('id_(.*?).html', url)[0]
                item["url"] = "http://player.youku.com/embed/" + vid
                item["source"] = "优酷视频"
                item["sourceUrl"] = "http://v.youku.com/v_show/id_" + vid + ".html"
                item["poster"] = None
                item["edition"] = None
                yield item

