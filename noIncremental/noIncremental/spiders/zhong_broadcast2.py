#coding=utf-8
import scrapy

from ..items import BroadcastItem, VideoItem
from scrapy.conf import settings
from noIncremental.spiders.beautifulSoup import processText
from bs4 import BeautifulSoup
import requests
import json
import re
import random

class NewsSpider(scrapy.Spider):

    name = "zhongbroad2"
    dict_news = {
    'i=8&c=entry&op=display&id=7&do=lesson&m=fy_lesson':'戏曲大全&京剧大全',
    'i=8&c=entry&op=display&id=26&do=lesson&m=fy_lesson':'戏曲大全&黄梅戏',
    'i=8&c=entry&op=display&id=40&do=lesson&m=fy_lesson':'戏曲大全&评剧',
    'i=8&c=entry&op=display&id=41&do=lesson&m=fy_lesson':'戏曲大全&豫剧',
    'i=8&c=entry&op=display&id=42&do=lesson&m=fy_lesson':'戏曲大全&越剧',
    'i=8&c=entry&op=display&id=122&do=lesson&m=fy_lesson':'戏曲大全&样板戏精选集',
    'i=8&c=entry&op=display&id=134&do=lesson&m=fy_lesson':'戏曲大全&粤剧',
    'i=8&c=entry&op=display&id=135&do=lesson&m=fy_lesson':'戏曲大全&昆区',
    'i=8&c=entry&op=display&id=136&do=lesson&m=fy_lesson':'戏曲大全&川剧',
    'i=8&c=entry&op=display&id=138&do=lesson&m=fy_lesson':'戏曲大全&楚剧',
    'i=8&c=entry&op=display&id=139&do=lesson&m=fy_lesson':'戏曲大全&秦腔',
    'i=8&c=entry&op=display&id=140&do=lesson&m=fy_lesson':'戏曲大全&绍剧',
    'i=8&c=entry&op=display&id=141&do=lesson&m=fy_lesson':'戏曲大全&沪剧',
    'i=8&c=entry&op=display&id=142&do=lesson&m=fy_lesson':'戏曲大全&吕剧',
    'i=8&c=entry&op=display&id=143&do=lesson&m=fy_lesson':'戏曲大全&淮剧',
    'i=8&c=entry&op=display&id=144&do=lesson&m=fy_lesson':'戏曲大全&河北梆子',
    'i=8&c=entry&op=display&id=145&do=lesson&m=fy_lesson':'戏曲大全&潮剧',
    'i=8&c=entry&op=display&id=146&do=lesson&m=fy_lesson':'戏曲大全&花鼓戏',
    'i=8&c=entry&op=display&id=147&do=lesson&m=fy_lesson':'戏曲大全&山东快书',
    'i=8&c=entry&op=display&id=148&do=lesson&m=fy_lesson':'戏曲大全&东北二人转',
    'i=8&c=entry&op=display&id=15&do=lesson&m=fy_lesson':'名著名篇&毛泽东诗词精选',
    'i=8&c=entry&op=display&id=60&do=lesson&m=fy_lesson':'名著名篇&中外诗歌散文选读',
    'i=8&c=entry&op=display&id=61&do=lesson&m=fy_lesson':'名著名篇&中外近代短篇小说选集',
    'i=8&c=entry&op=display&id=62&do=lesson&m=fy_lesson':'名著名篇&红楼梦诗词诵读',
    'i=8&c=entry&op=display&id=25&do=lesson&m=fy_lesson':'名著名篇&鲁迅文集',
    'i=8&c=entry&op=display&id=43&do=lesson&m=fy_lesson':'名著名篇&鲁迅-呐喊',
    'i=8&c=entry&op=display&id=44&do=lesson&m=fy_lesson':'名著名篇&鲁迅-彷徨',
    'i=8&c=entry&op=display&id=45&do=lesson&m=fy_lesson':'名著名篇&钱钟书-围城',
    'i=8&c=entry&op=display&id=46&do=lesson&m=fy_lesson':'名著名篇&老舍-茶馆',
    'i=8&c=entry&op=display&id=47&do=lesson&m=fy_lesson':'名著名篇&老舍-骆驼祥子',
    'i=8&c=entry&op=display&id=48&do=lesson&m=fy_lesson':'名著名篇&矛盾-子夜',
    'i=8&c=entry&op=display&id=49&do=lesson&m=fy_lesson':'名著名篇&林海音-城南旧事',
    'i=8&c=entry&op=display&id=50&do=lesson&m=fy_lesson':'名著名篇&徐志摩-散文诗集',
    'i=8&c=entry&op=display&id=51&do=lesson&m=fy_lesson':'名著名篇&中国近代名家散文选',
    'i=8&c=entry&op=display&id=52&do=lesson&m=fy_lesson':'文学经典&红楼梦-原文诵读',
    'i=8&c=entry&op=display&id=53&do=lesson&m=fy_lesson':'文学经典&三国演义-原文诵读',
    'i=8&c=entry&op=display&id=54&do=lesson&m=fy_lesson':'文学经典&西游记-原文诵读',
    'i=8&c=entry&op=display&id=55&do=lesson&m=fy_lesson':'文学经典&水浒传-原文诵读',
    'i=8&c=entry&op=display&id=57&do=lesson&m=fy_lesson':'文学经典&唐诗三百首',
    'i=8&c=entry&op=display&id=58&do=lesson&m=fy_lesson':'文学经典&宋词三百首',
    'i=8&c=entry&op=display&id=68&do=lesson&m=fy_lesson':'相声评书&马季相声大全',
    'i=8&c=entry&op=display&id=69&do=lesson&m=fy_lesson':'相声评书&侯耀文相声全集',
    'i=8&c=entry&op=display&id=70&do=lesson&m=fy_lesson':'相声评书&郭德钢相声十年经典',
    'i=8&c=entry&op=display&id=232&do=lesson&m=fy_lesson':'相声评书&春晚相声小品大全',
    'i=8&c=entry&op=display&id=65&do=lesson&m=fy_lesson':'国学佛学&圣贤教育改变命运',
    'i=8&c=entry&op=display&id=66&do=lesson&m=fy_lesson':'国学佛学&听佛-佛教故事',
    'i=8&c=entry&op=display&id=67&do=lesson&m=fy_lesson':'国学佛学&左手参禅-右手修佛',
    'i=8&c=entry&op=display&id=150&do=lesson&m=fy_lesson':'国学佛学&佛号',
    'i=8&c=entry&op=display&id=151&do=lesson&m=fy_lesson':'国学佛学&佛渡有缘人',
    'i=8&c=entry&op=display&id=152&do=lesson&m=fy_lesson':'国学佛学&叩佛问禅'
}
    start_urls = ['http://wx.letuizu.com/app/index.php?%s' % x for x in dict_news.keys()]

    def parse(self, response):
        soup = BeautifulSoup(response.text, "lxml")
        next_requests = list()

        for infoDiv in soup.find_all(attrs={"class": "course-chapter"})[1].find_all('li'):
            item = BroadcastItem()
            item["title"] = infoDiv.a.get_text() # 标题
            try:
                item["edition"] = re.findall(r"\d+\d*",infoDiv.a.get_text())[0]
            except:
                print "no edition"
                item["edition"] = None
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
