#coding=utf-8
import scrapy
from ..items import VideoItem
import re

#Code: Tom Tang
class WeChatSpider(scrapy.Spider):
    name = "xuehulusi"
    start_urls = ['https://mp.weixin.qq.com/s?__biz=MzIzMTcyMzY4OA==&mid=2247485475&idx=6&sn=a70d3b3691b24fe63035b561e3cf9b44&chksm=e89e8fe4dfe906f2d09c204bd0795183f875a9b5f6caa2b8e7b0e96872f8a08ee3da7322a1d3&scene=21#wechat_redirect']

    def parse(self, response):
        urls_ori = response.xpath('//*[@id="js_content"]/section[4]/section/section/section[2]/section/section/section//a/@href | //*[@id="js_content"]/section[5]/section/section/section[2]/section/section/section//a/@href').extract()
        url_lists = list(set(urls_ori))
        for url_next in url_lists:
            if url_next.split('.')[1] == "youku":
                req = scrapy.Request(url=url_next, callback=self.youku_parseinfo)
                item = VideoItem()
                item["sourceUrl"] = url_next
                req.meta["m_item"] = item
                yield req

    def youku_parseinfo(self, response):
        page_url = response.url
        vid = page_url.split('?')[0].split('/')[-1].split('.')[0].split('_')[-1]
        url = "http://player.youku.com/embed/" + vid
        title = response.xpath('//div[@class="base_info"]/h1/@title').extract()[0]
        item1 = response.meta["m_item"]
        item1["module"] = "兴趣爱好"
        item1["title"] = title
        item1["source"] = "优酷视频"
        item1["url"] = url
        item1["poster"] = None
        item1["edition"] = None
        item1["className"] = "学葫芦丝"

        yield item1