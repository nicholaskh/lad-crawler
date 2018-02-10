# coding=utf-8
import scrapy
import re

from ..items import VideoItem


class newsSpider(scrapy.Spider):
    name = "yangshengcao"
    start_urls = ['https://mp.weixin.qq.com/s?__biz=MzIzMTcyMzY4OA==&mid=2247488169&idx=2&sn=3b3233263d3416297ce65b821f347d33&chksm=e89e956edfe91c786c0e893fd80c47a364680e56511737b7a0101edc546153356f7c5a52a3ef&scene=21#wechat_redirect']

    def parse(self, response):
        alabels = response.xpath('//section[@style="display: inline-table;border-collapse: collapse;table-layout: fixed;width: 100%;box-sizing: border-box;"]//a')
        for alabel in alabels:
            titles = alabel.xpath('.//strong/text()').extract()
            href = alabel.xpath('@href').extract_first()
            if titles is not None and "dwz.cn" in href:
                title = ",".join(titles)
                req = scrapy.Request(url=href, callback=self.parse_url)
                req.meta['title'] = title
                yield req

    def parse_url(self, response):
        item = VideoItem()
        item["module"] = "养生讲坛"
        item['className'] = "养生操"
        url = response.xpath('//iframe[@class="video_iframe"]/@data-src').extract_first()
        if url is not None:
            item["title"] = response.meta['title']
            item["url"] = url.split('&')[0].replace("preview", "player") + "&tiny=0&auto=0"
            item["source"] = "腾讯视频"
            item["sourceUrl"] = response.url
            item["poster"] = None
            item["edition"] = None
            yield item
