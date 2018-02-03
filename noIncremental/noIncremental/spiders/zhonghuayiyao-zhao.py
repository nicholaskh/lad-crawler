# coding=utf-8
import scrapy
import re

from ..items import VideoItem


class newsSpider(scrapy.Spider):
    name = "zhonghuayiyao"
    start_urls = [
        'https://mp.weixin.qq.com/s?__biz=MzIzMTcyMzY4OA==&mid=2247484055&idx=4&sn=21ca96c64447d8cbb3e76bd2c9e410ed&chksm=e89e8550dfe90c46c13f767f6b493fb9595ddac230357ffaabc81d8563919fb8b4f1f12340a5&mpshare=1&scene=1&srcid=120247gA9fb0onWeS3K3uP5H&pass_ticket=ETzscQemVtZ6bwgJRRIepwgeWsLJ0TLI%2FbX7bjltdspch27wlrDnxzA5vUivZMG7#rd']

    def parse(self, response):
        urls = response.xpath('//li/p/a[@style]/@href').extract()

        for url in urls:
            yield scrapy.Request(url=url, callback=self.parse_pid)

    def parse_pid(self, response):
        pid = re.findall('videoCenterId","(.+)"', response.text)[0]
        info_url = "http://vdn.apps.cntv.cn/api/getHttpVideoInfo.do?pid=" + pid
        req = scrapy.Request(url=info_url, callback=self.parse_info)
        req.meta['sourceUrl'] = response.url
        yield req

    def parse_info(self, response):
        sourceUrl = response.meta['sourceUrl']
        item = VideoItem()
        item["module"] = "养生论坛"
        item["className"] = "中华医药"
        item["title"] = re.findall('title":"(.*?)"', response.text)[0].split(" ")[-1]
        item["source"] = "中国网络电视台CNTV"
        item["sourceUrl"] = sourceUrl
        urls = re.findall('jpg","url":"(.*?)"', response.text)
        # 取最后的清晰度
        last_num = 1000
        for i in range(0, urls.__len__())[::-1]:
            num = int(urls[i].split('-')[-1].split('.')[0], 10)
            if num > last_num:
                item["url"] = urls[i + 1:]
                break
            elif i == 0:
                item["url"] = urls
                break
            else:
                last_num = num
        item["poster"] = None
        item["edition"] = None
        yield item
