#coding=utf-8
import scrapy
from ..items import VideoItem
import re

#Code: Tom Tang
class WeChatSpider(scrapy.Spider):
    name = "xuetaiji"
    start_urls = ['https://mp.weixin.qq.com/s?__biz=MzIzMTcyMzY4OA==&mid=2247484358&idx=6&sn=771619d53beb26c7096f6c21dd7f324e&scene=21#wechat_redirect']

    def parse(self, response):
        url_ori = response.xpath('//*[@id="js_content"]/section[2]//a/@href | //*[@id="js_content"]/section[3]//a/@href').extract()
        url_lists = list(set(url_ori))
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
        item1["className"] = "学太极"
        item1["title"] = title
        item1["source"] = "优酷视频"
        item1["url"] = url
        item1["poster"] = None
        item1["edition"] = None

        yield item1