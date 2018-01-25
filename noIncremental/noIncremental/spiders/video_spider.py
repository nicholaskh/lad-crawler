#coding=utf-8
import scrapy

from ..items import BroadcastItem, VideoItem
from scrapy.conf import settings
from noIncremental.spiders.beautifulSoup import processText
from bs4 import BeautifulSoup
import requests
import re
import json
import random

class NewsSpider(scrapy.Spider):

    name = "videotest"
    dict_news = {
    'i=8&c=entry&op=display&id=96&do=lesson&m=fy_lesson':'营养课堂&饮食与养生',
    'i=8&c=entry&op=display&id=219&do=lesson&m=fy_lesson':'名医讲座&冠心病重点预防',
    'i=8&c=entry&op=display&id=72&do=lesson&m=fy_lesson':'名医讲座&更年期常识',
    'i=8&c=entry&op=display&id=101&do=lesson&m=fy_lesson':'养生讲坛&国学与养生',
    'i=8&c=entry&op=display&id=223&do=lesson&m=fy_lesson':'养生讲坛&体质养生',
    'i=8&c=entry&op=display&id=225&do=lesson&m=fy_lesson':'养生讲坛&揭秘艺术医疗',
    'i=8&c=entry&op=display&id=189&do=lesson&m=fy_lesson':'家庭救护&家庭急救必备常识二',
    'i=8&c=entry&op=display&id=194&do=lesson&m=fy_lesson':'健康食谱&养生菜谱',
    'i=8&c=entry&op=display&id=190&do=lesson&m=fy_lesson':'健康食谱&凉菜菜谱',
    'i=8&c=entry&op=display&id=177&do=lesson&m=fy_lesson':'教育法律&心灵和谐五则',
    'i=8&c=entry&op=display&id=178&do=lesson&m=fy_lesson':'教育法律&阳光心态十二讲',
    'i=8&c=entry&op=display&id=179&do=lesson&m=fy_lesson':'教育法律&情绪管理 压力应对',
    'i=8&c=entry&op=display&id=180&do=lesson&m=fy_lesson':'教育法律&人际交往 从心开始',
    'i=8&c=entry&op=display&id=181&do=lesson&m=fy_lesson':'教育法律&传统经典 修身育人',
    'i=8&c=entry&op=display&id=182&do=lesson&m=fy_lesson':'教育法律&国学应用 人际和谐',
    'i=8&c=entry&op=display&id=183&do=lesson&m=fy_lesson':'教育法律&国学中的管理之道',
    'i=8&c=entry&op=display&id=18&do=lesson&m=fy_lesson':'节目展演&第一届中老年模特大赛',
    'i=8&c=entry&op=display&id=63&do=lesson&m=fy_lesson':'节目展演&第二届中老年模特大赛',
    'i=8&c=entry&op=display&id=19&do=lesson&m=fy_lesson':'节目展演&第一届中老年艺术节',
    'i=8&c=entry&op=display&id=20&do=lesson&m=fy_lesson':'节目展演&第二届中老年艺术节',
    'i=8&c=entry&op=display&id=21&do=lesson&m=fy_lesson':'节目展演&第三届中老年艺术节',
    'i=8&c=entry&op=display&id=22&do=lesson&m=fy_lesson':'节目展演&乐退族春晚选拔赛',
    'i=8&c=entry&op=display&id=216&do=lesson&m=fy_lesson':'广场舞&广场舞欣赏',
    'i=8&c=entry&op=display&id=241&do=lesson&m=fy_lesson':'广场舞&水兵舞专辑',
    'i=8&c=entry&op=display&id=184&do=lesson&m=fy_lesson':'兴趣爱好&学摄影'
}
    start_urls = ['http://wx.letuizu.com/app/index.php?%s' % x for x in dict_news.keys()]

    def parse(self, response):

        headers1 = {
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Encoding': 'gzip, deflate, sdch',
            'Accept-Language': 'zh-CN,zh;q=0.8,en;q=0.6',
            'Cache-Control': 'max-age=0',
            'Proxy-Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1',
            'User-Agent': random.choice(settings["USER_AGENTS"])
        }
        soup = BeautifulSoup(response.text, "lxml")

        next_requests = list()

        for infoDiv in soup.find_all(attrs={"class": "course-chapter"})[1].find_all('li')[1:]:
            item = VideoItem()
            item["title"] = infoDiv.a.get_text() # 标题
            try:
                if len(re.findall(r"\d+\d*",infoDiv.a.get_text())) > 0:
                    item["edition"] = re.findall(r"\d+\d*",infoDiv.a.get_text())[0]
                else:
                    item["edition"] = re.search('第(.+)集', item["title"].encode('utf-8')).group(1)
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
        headers1 = {
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Encoding': 'gzip, deflate, sdch',
            'Accept-Language': 'zh-CN,zh;q=0.8,en;q=0.6',
            'Cache-Control': 'max-age=0',
            'Proxy-Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1',
            'User-Agent': random.choice(settings["USER_AGENTS"])
        }

        murl = response.url
        html = requests.get(murl, headers=headers1).text

        item = response.meta['item']
        # html = response.text
        part_info = json.loads(html)["code"]
        soup = BeautifulSoup(part_info,'lxml')
        item["source"] = '乐退族 中老年养生大学'
        try:
            item["url"] = soup.find('video').get('src')
        except:
            item["url"] = soup.find('iframe').get('src')
        try:
            item["poster"] = soup.find('video').get('poster')
        except:
            try:
                item["poster"] = soup.find('iframe').get('poster')
            except:
                item["poster"] = None
        yield item
