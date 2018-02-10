# coding=utf-8
import scrapy
import json

from ..items import VideoItem


class newsSpider(scrapy.Spider):
    name = "zhongguotongshi"
    start_urls = ['https://mp.weixin.qq.com/s?__biz=MzIzMTcyMzY4OA==&mid=2247492234&idx=7&sn=f83ee8336ca91932d3a00a5bc68d0520&chksm=e89d654ddfeaec5b7e2463ead33977d3a03908ed9f54f0e5be78d00bef9791952a59b0aa07ce&mpshare=1&scene=1&srcid=0207FJxn5Cs8gpggqAuwSGCi&pass_ticket=X8hh%2BMszHop5erYieQ5sy2NnGUGla5ehPpR0QWm10V7j9q%2F6jjdgWbNe0pztUhJZ#rd']

    def parse(self, response):
        hrefs = response.xpath('//section[@style="transform: translate3d(0px, 0px, 0px);-webkit-transform: translate3d(0px, 0px, 0px);-moz-transform: translate3d(0px, 0px, 0px);-o-transform: translate3d(0px, 0px, 0px);text-align: center;box-sizing: border-box;"]//a/@href').extract()
        urls = list(set(hrefs))
        for url in urls:
            req = scrapy.Request(url=url, callback=self.parse_objectid)
            yield req

    def parse_objectid(self, response):
        data = response.xpath('//iframe/@data').extract_first()
        params = json.loads(data)
        object_id = params['objectid']
        title = response.xpath('//*[@id="contentBox"]/p[1]/strong/span/text()').extract_first()
        if object_id is not None and title is not None:
            url = "http://mooc1-api.chaoxing.com/ananas/status/" + object_id
            req = scrapy.Request(url=url, callback=self.parse_url)
            req.meta['source_url'] = response.url
            req.meta['title'] = title
            yield req

    # 超星视频
    def parse_url(self, response):
        item = VideoItem()
        item["module"] = "教育法律"
        item['className'] = "中国通史"
        item["title"] = response.meta['title']
        url = json.loads(response.text)['httphd']
        if url is not None:
            item["url"] = url
            item["source"] = "超星"
            item["sourceUrl"] = response.meta['source_url']
            item["poster"] = None
            item["edition"] = None
            yield item
