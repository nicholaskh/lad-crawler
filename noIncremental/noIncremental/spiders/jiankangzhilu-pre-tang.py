#coding=utf-8
import scrapy
from ..items import VideoItem
import re

#Code: Tom Tang
class WeChatSpider(scrapy.Spider):
    name = "jiankangzhilu-pre"
    start_urls = ['https://mp.weixin.qq.com/s?__biz=MzIzMTcyMzY4OA==&mid=2247483847&idx=1&sn=0b75ba3b914a29860a04a4de5c7e1966&chksm=e89e8600dfe90f16f554775f547d2c53b540a8682328cdd18ba40918f7f56dc73a400e810c10&mpshare=1&scene=1&srcid=0207pplJKe21UNEvUq3EFanZ&pass_ticket=X8hh%2BMszHop5erYieQ5sy2NnGUGla5ehPpR0QWm10V7j9q%2F6jjdgWbNe0pztUhJZ#rd']

    def parse(self, response):
        url_ori1 = response.xpath('//*[@id="js_content"]/section[2]/section[2]/section/section[2]/section/section/section/section/p')
        url_ori2 = response.xpath('//*[@id="js_content"]/section[2]/section[4]/section/section[2]/section/section/section/section/p')
        url_ori3 = response.xpath('//*[@id="js_content"]/section[2]/section[6]/section/section[2]/section/section/section/section/p')
        url_ori4 = response.xpath('//*[@id="js_content"]/section[2]/section[8]/section/section[2]/section/section/section/section/p')

        for i in range(len(url_ori1)):
            data = url_ori1[i].extract()
            page_url = re.findall(r'<a href="(.*?)"',data)
            if len(page_url) == 0:
                continue

            title = re.findall(r'<strong>(.*?)</strong>',data)
            if len(title) == 0:
                title = re.findall(r'\);">(.*?)</a>',data)

            if page_url[0].split('.')[1] == "qq":
                vid = page_url[0].split('/')[-1].split('.')[0]
                url = "https://v.qq.com/iframe/player.html?vid=" + vid + "&tiny=0&auto=0"

                item = VideoItem()
                item["module"] = "养生讲坛"
                item["className"] = "健康之路"
                item["title"] = "2011-" + title[0]
                item["source"] = "腾讯视频"
                item["sourceUrl"] = page_url[0]
                item["url"] = url
                item["poster"] = None
                item["edition"] = None

                yield item

        for i in range(len(url_ori2)):
            data = url_ori2[i].extract()
            page_url = re.findall(r'<a href="(.*?)"',data)
            if len(page_url) == 0:
                continue

            title = re.findall(r'<strong>(.*?)</strong>',data)
            if len(title) == 0:
                title = re.findall(r'\);">(.*?)</a>',data)

            if page_url[0].split('.')[1] == "qq":
                vid = page_url[0].split('/')[-1].split('.')[0]
                url = "https://v.qq.com/iframe/player.html?vid=" + vid + "&tiny=0&auto=0"

                item = VideoItem()
                item["module"] = "养生讲坛"
                item["className"] = "健康之路"
                item["title"] = "2012-" + title[0]
                item["source"] = "腾讯视频"
                item["sourceUrl"] = page_url[0]
                item["url"] = url
                item["poster"] = None
                item["edition"] = None

                yield item

        for i in range(len(url_ori3)):
            data = url_ori3[i].extract()
            page_url = re.findall(r'<a href="(.*?)"',data)
            if len(page_url) == 0:
                continue

            title = re.findall(r'<strong>(.*?)</strong>',data)
            if len(title) == 0:
                title = re.findall(r'\);">(.*?)</a>',data)

            if page_url[0].split('.')[1] == "qq":
                vid = page_url[0].split('/')[-1].split('.')[0]
                url = "https://v.qq.com/iframe/player.html?vid=" + vid + "&tiny=0&auto=0"

                item = VideoItem()
                item["module"] = "养生讲坛"
                item["className"] = "健康之路"
                item["title"] = "2013-" + title[0]
                item["source"] = "腾讯视频"
                item["sourceUrl"] = page_url[0]
                item["url"] = url
                item["poster"] = None
                item["edition"] = None

                yield item

        for i in range(len(url_ori4)):
            data = url_ori4[i].extract()
            page_url = re.findall(r'<a href="(.*?)"',data)
            if len(page_url) == 0:
                continue

            title = re.findall(r'<strong>(.*?)</strong>',data)
            if len(title) == 0:
                title = re.findall(r'\);">(.*?)</a>',data)

            if page_url[0].split('.')[1] == "qq":
                vid = page_url[0].split('/')[-1].split('.')[0]
                url = "https://v.qq.com/iframe/player.html?vid=" + vid + "&tiny=0&auto=0"

                item = VideoItem()
                item["module"] = "养生讲坛"
                item["className"] = "健康之路"
                item["title"] = "2014-" + title[0]
                item["source"] = "腾讯视频"
                item["sourceUrl"] = page_url[0]
                item["url"] = url
                item["poster"] = None
                item["edition"] = None

                yield item