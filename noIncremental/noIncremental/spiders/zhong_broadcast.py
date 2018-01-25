#coding=utf-8
import scrapy

from ..items import BroadcastItem, VideoItem
from scrapy.conf import settings
from noIncremental.spiders.beautifulSoup import processText
from bs4 import BeautifulSoup
import re
import requests
import json
import random

class NewsSpider(scrapy.Spider):

    name = "zhongbroad"
    dict_news = {
    'i=8&c=entry&op=display&id=115&do=lesson&m=fy_lesson':'养生广播&养生书籍书摘',
    'i=8&c=entry&op=display&id=116&do=lesson&m=fy_lesson':'养生广播&人人都能活到100岁',
    'i=8&c=entry&op=display&id=117&do=lesson&m=fy_lesson':'养生广播&老年健康长寿知识讲座',
    'i=8&c=entry&op=display&id=118&do=lesson&m=fy_lesson':'养生广播&新世纪健康饮食',
    'i=8&c=entry&op=display&id=119&do=lesson&m=fy_lesson':'养生广播&求医不如求己大全集',
    'i=8&c=entry&op=display&id=31&do=lesson&m=fy_lesson':'音乐大全&班得瑞轻音乐',
    'i=8&c=entry&op=display&id=32&do=lesson&m=fy_lesson':'音乐大全&调心静修组曲',
    'i=8&c=entry&op=display&id=34&do=lesson&m=fy_lesson':'音乐大全&梁祝乐器演奏',
    'i=8&c=entry&op=display&id=35&do=lesson&m=fy_lesson':'音乐大全&古典音乐精选',
    'i=8&c=entry&op=display&id=123&do=lesson&m=fy_lesson':'音乐大全&古筝49首',
    'i=8&c=entry&op=display&id=124&do=lesson&m=fy_lesson':'音乐大全&琵琶45首',
    'i=8&c=entry&op=display&id=125&do=lesson&m=fy_lesson':'音乐大全&笛子54首',
    'i=8&c=entry&op=display&id=127&do=lesson&m=fy_lesson':'音乐大全&江南丝竹',
    'i=8&c=entry&op=display&id=128&do=lesson&m=fy_lesson':'音乐大全&天籁佛音',
    'i=8&c=entry&op=display&id=131&do=lesson&m=fy_lesson':'音乐大全&世界钢琴名曲',
    'i=8&c=entry&op=display&id=133&do=lesson&m=fy_lesson':'音乐大全&养生音乐汇',
    'i=8&c=entry&op=display&id=156&do=lesson&m=fy_lesson':'音乐大全&五行音乐',
    'i=8&c=entry&op=display&id=169&do=lesson&m=fy_lesson':'音乐大全&小提琴曲',
    'i=8&c=entry&op=display&id=170&do=lesson&m=fy_lesson':'音乐大全&大提琴曲',
    'i=8&c=entry&op=display&id=171&do=lesson&m=fy_lesson':'音乐大全&萨克斯',
    'i=8&c=entry&op=display&id=174&do=lesson&m=fy_lesson':'音乐大全&中国古典乐器演奏',
    'i=8&c=entry&op=display&id=27&do=lesson&m=fy_lesson':'音乐大全&民族器乐',
    'i=8&c=entry&op=display&id=28&do=lesson&m=fy_lesson':'音乐大全&二胡46首',
    'i=8&c=entry&op=display&id=227&do=lesson&m=fy_lesson':'歌曲大全&军旅歌曲精选',
    'i=8&c=entry&op=display&id=228&do=lesson&m=fy_lesson':'歌曲大全&老电影歌曲',
    'i=8&c=entry&op=display&id=229&do=lesson&m=fy_lesson':'歌曲大全&春晚金曲',
    'i=8&c=entry&op=display&id=230&do=lesson&m=fy_lesson':'歌曲大全&经典民歌',
    'i=8&c=entry&op=display&id=231&do=lesson&m=fy_lesson':'歌曲大全&经典红歌',
    'i=8&c=entry&op=display&id=226&do=lesson&m=fy_lesson':'歌曲大全&知情之歌',
    'i=8&c=entry&op=display&id=39&do=lesson&m=fy_lesson':'歌曲大全&苏俄歌曲',
    'i=8&c=entry&op=display&id=38&do=lesson&m=fy_lesson':'歌曲大全&经典老歌',
    'i=8&c=entry&op=display&id=37&do=lesson&m=fy_lesson':'歌曲大全&老歌新唱',
    'i=8&c=entry&op=display&id=36&do=lesson&m=fy_lesson':'歌曲大全&东方红舞蹈史诗',
    'i=8&c=entry&op=display&id=64&do=lesson&m=fy_lesson':'歌曲大全&宝宝的异想世界'
}
    start_urls = ['http://wx.letuizu.com/app/index.php?%s' % x for x in dict_news.keys()]

    def parse(self, response):
        soup = BeautifulSoup(response.text, "lxml")
        next_requests = list()

        for infoDiv in soup.find_all(attrs={"class": "course-chapter"})[1].find_all('li'):
            item = BroadcastItem()
            item["title"] = infoDiv.a.get_text() # 标题
            item["edition"] = re.findall(r"\d+\d*",infoDiv.a.get_text())[0]
            item["sourceUrl"] = response.url
            dic_key = response.url.split('?')[1]
            dic_value = self.dict_news[dic_key]
            item["module"] = dic_value.split('&')[0]
            item["className"] = dic_value.split('&')[1]
            next_info_url = infoDiv.a.get('href')
            i = next_info_url.split('&')[0].split('=')[1]
            c = next_info_url.split('&')[1].split('=')[1]
            id_num = next_info_url.split('&')[2].split('=')[1]
            sectionid = next_info_url.split('&')[3].split('=')[1]
            next_url = 'http://wx.letuizu.com/app/index.php?i=' + i + '&c=' + c + '&id=' + id_num + '&sectionid=' + sectionid + '&do=ajaxlesson&m=fy_lesson'
            req = scrapy.Request(url=next_url, callback=self.parse_info)
            req.meta['item'] = item
            next_requests.append(req)
        for req in next_requests:
            yield req


    def parse_info(self, response):
        html = response.text
        item = response.meta['item']
        part_info = json.loads(html)["code"]
        soup = BeautifulSoup(part_info,'lxml')
        item["source"] = '乐退族 中老年养生大学'
        try:
            item["broadcast_url"] = soup.find('audio').get('src')
        except:
            print('no information')
        yield item
