# coding=utf-8
import scrapy
import re

from ..items import BroadcastItem


class newsSpider(scrapy.Spider):
    name = "jingdianlaoge2000"
    start_urls = ['https://mp.weixin.qq.com/s?__biz=MzIzMTcyMzY4OA==&mid=2247486048&idx=3&sn=7b4748540cba44566f707da5453b28b5&chksm=e89e8da7dfe904b154f4181d46707d0a27b88187c81b2a43edc37957aa955b8e40df757cb62f&mpshare=1&scene=1&srcid=1202Z69BuCZqRDGe740vLS91&pass_ticket=ETzscQemVtZ6bwgJRRIepwgeWsLJ0TLI%2FbX7bjltdspch27wlrDnxzA5vUivZMG7#rd']

    def parse(self, response):
        urls = response.xpath('//*[@id="js_content"]/section[2]//a/@href').extract()

        for url in urls:
            req = scrapy.Request(url=url, callback=self.parse_music)
            yield req


    def parse_music(self, response):
        musics = response.xpath('//qqmusic')
        for music in musics:
            item = BroadcastItem()
            item["module"] = "歌唱家"
            item["className"] = music.xpath('@singer').extract_first().split('-')[0].strip()
            item["title"] = music.xpath('@music_name').extract_first()
            item["source"] = "qq音乐"
            item["sourceUrl"] = response.url
            item["intro"] = music.xpath('@singer').extract_first()
            item["broadcast_url"] = music.xpath('@audiourl').extract_first()
            item["edition"] = None
            yield item