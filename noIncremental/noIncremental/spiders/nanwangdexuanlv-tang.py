#coding=utf-8
import scrapy
import re
from ..items import BroadcastItem

#Code: Tom Tang
class WeChatSpider(scrapy.Spider):
    name = "nanwangdexuanlv"
    start_urls = ["https://mp.weixin.qq.com/s/TWSY1rz5zBHVh_wLIkKhdQ"]

    def parse(self, response):
        #Process the music
        mu_name = response.xpath('//*[@id="js_content"]/section[2]/section//qqmusic/@music_name').extract()
        mu_singer = response.xpath('//*[@id="js_content"]/section[2]/section//qqmusic/@singer').extract()
        mu_url = response.xpath('//*[@id="js_content"]/section[2]/section//qqmusic/@audiourl').extract()
        for i in range(len(mu_name)):
            if "qq.com" in mu_url[i]:
                item = BroadcastItem()
                item["module"] = "广播"
                item["className"] = "知青岁月"
                item["title"] = mu_name[i]
                item["sourceUrl"] = response.url
                item["broadcast_url"] = mu_url[i]
                item["source"] = "QQ音乐"
                item["intro"] = mu_singer[i]
                yield item