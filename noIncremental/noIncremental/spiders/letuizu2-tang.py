#coding=utf-8
import scrapy
from ..items import VideoItem
import requests
import json
import re
import random

#Code: Tom Tang
class LetuizuSpider(scrapy.Spider):
    name = "letuizu2"
    start_urls = ["http://wx.letuizu.com/app/index.php?i=8&c=entry&op=display&id=267&do=lesson&m=fy_lesson",
                  "http://wx.letuizu.com/app/index.php?i=8&c=entry&op=display&id=214&do=lesson&m=fy_lesson",
                  "http://wx.letuizu.com/app/index.php?i=8&c=entry&op=display&id=185&do=lesson&m=fy_lesson",
                  "http://wx.letuizu.com/app/index.php?i=8&c=entry&op=display&id=186&do=lesson&m=fy_lesson",
                  "http://wx.letuizu.com/app/index.php?i=8&c=entry&op=display&id=187&do=lesson&m=fy_lesson",
                  "http://wx.letuizu.com/app/index.php?i=8&c=entry&op=display&id=213&do=lesson&m=fy_lesson",
                  "http://wx.letuizu.com/app/index.php?i=8&c=entry&op=display&id=266&do=lesson&m=fy_lesson",
                  "http://wx.letuizu.com/app/index.php?i=8&c=entry&op=display&id=258&do=lesson&m=fy_lesson",
                  "http://wx.letuizu.com/app/index.php?i=8&c=entry&op=display&id=254&do=lesson&m=fy_lesson",
                  "http://wx.letuizu.com/app/index.php?i=8&c=entry&op=display&id=242&do=lesson&m=fy_lesson",
                  "http://wx.letuizu.com/app/index.php?i=8&c=entry&op=display&id=253&do=lesson&m=fy_lesson",
                  "http://wx.letuizu.com/app/index.php?i=8&c=entry&op=display&id=252&do=lesson&m=fy_lesson",
                  "http://wx.letuizu.com/app/index.php?i=8&c=entry&op=display&id=196&do=lesson&m=fy_lesson",
                  "http://wx.letuizu.com/app/index.php?i=8&c=entry&op=display&id=197&do=lesson&m=fy_lesson",
                  "http://wx.letuizu.com/app/index.php?i=8&c=entry&op=display&id=198&do=lesson&m=fy_lesson",
                  "http://wx.letuizu.com/app/index.php?i=8&c=entry&op=display&id=199&do=lesson&m=fy_lesson",
                  "http://wx.letuizu.com/app/index.php?i=8&c=entry&op=display&id=200&do=lesson&m=fy_lesson",
                  "http://wx.letuizu.com/app/index.php?i=8&c=entry&op=display&id=201&do=lesson&m=fy_lesson",
                  "http://wx.letuizu.com/app/index.php?i=8&c=entry&op=display&id=202&do=lesson&m=fy_lesson",
                  "http://wx.letuizu.com/app/index.php?i=8&c=entry&op=display&id=203&do=lesson&m=fy_lesson",
                  "http://wx.letuizu.com/app/index.php?i=8&c=entry&op=display&id=204&do=lesson&m=fy_lesson",
                  "http://wx.letuizu.com/app/index.php?i=8&c=entry&op=display&id=205&do=lesson&m=fy_lesson",
                  "http://wx.letuizu.com/app/index.php?i=8&c=entry&op=display&id=206&do=lesson&m=fy_lesson",
                  "http://wx.letuizu.com/app/index.php?i=8&c=entry&op=display&id=207&do=lesson&m=fy_lesson",
                  "http://wx.letuizu.com/app/index.php?i=8&c=entry&op=display&id=208&do=lesson&m=fy_lesson",
                  "http://wx.letuizu.com/app/index.php?i=8&c=entry&op=display&id=209&do=lesson&m=fy_lesson",
                  "http://wx.letuizu.com/app/index.php?i=8&c=entry&op=display&id=273&do=lesson&m=fy_lesson",
                  "http://wx.letuizu.com/app/index.php?i=8&c=entry&op=display&id=274&do=lesson&m=fy_lesson",
                  "http://wx.letuizu.com/app/index.php?i=8&c=entry&op=display&id=275&do=lesson&m=fy_lesson",
                  "http://wx.letuizu.com/app/index.php?i=8&c=entry&op=display&id=278&do=lesson&m=fy_lesson"
]

    def parse(self, response):
        data = response.xpath('//div[@class="course-container"]/div[3]/ul/li/ul//li').extract()
        for each in data:
            item = VideoItem()
            item["module"] = "兴趣爱好"
            item["className"] = response.xpath('//div[@class="course-container"]/div[3]/ul/li/h2/text()').extract()[0].split('[')[0]
            item["title"] = re.findall(r'>.*?</a>', each)[0][1:-4]
            item["source"] = "乐退族 中老年养生大学"
            item["sourceUrl"] = response.url
            item["poster"] = None
            item["edition"] = None

            url = re.findall(r'<a href=".*?"',each)[0][9:-1]
            i = each.split('&')[0].split('=')[1]
            c = each.split('&')[1].split('=')[1]
            id_num = each.split('&')[2].split('=')[1]
            sectionid = each.split('&')[3].split('=')[1]
            next_url = 'http://wx.letuizu.com/app/index.php?i=' + i + '&c=' + c + '&id=' + id_num + '&sectionid=' + sectionid + '&do=ajaxlesson&m=fy_lesson'
            req = scrapy.Request(url=next_url, callback=self.parse_url)
            req.meta["m_item"] = item
            yield req

    def parse_url(self, response):
        info = json.loads(response.text)["code"]
        m_item = response.meta['m_item']
        url_ori = re.findall(r'src=.*?;',info)
        if len(url_ori) != 0:
            url = url_ori[0][4:-1]
        else:
            url_ori = re.findall(r'src=".*?"',info)
            url = url_ori[0][5:-1]

        m_item["url"] = url
        yield m_item
