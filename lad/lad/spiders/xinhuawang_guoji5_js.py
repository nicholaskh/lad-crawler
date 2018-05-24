#coding=utf-8
import scrapy
import json
import re

from ..items import DailyNewsItem
from ..spiders.beautifulSoup import processText, processImgSep
from datetime import datetime
from .basespider import BaseTimeCheckSpider

class newsSpider(BaseTimeCheckSpider):
    name = "xinhuawang_guoji5"
    start_urls = ['http://sg.news.cn/scdt.htm',
                  'http://sg.news.cn/zxjl.htm',
                  'http://sg.news.cn/ydyl.htm',
                  'http://sg.news.cn/scdh.htm',
                  'http://sg.news.cn/ycsd.htm',
                  'http://sg.news.cn/scqw.htm',
                  'http://sg.news.cn/cjyw.htm',
                  'http://sg.news.cn/scjy.htm',
                  'http://sg.news.cn/xhjzzl.htm',
                  'http://sg.news.cn/rdzt.htm',
                  'http://sg.news.cn/lyzx.htm']

    def parse(self, response):
        nid = re.findall('pageNid":\["(.*?)"', response.text)[-1]
        url = "http://qc.wa.news.cn/nodeart/list?nid=" + nid + "&pgnum=1&cnt=40"
        req = scrapy.Request(url=url, callback=self.parse_url)
        yield req

    def parse_url(self, response):
        data = json.loads(response.text.strip('(').strip(')'))
        times = []
        urls = []
        for row in data["data"]["list"]:
            times.append(row["PubTime"].split(' ')[0])
            url = row["LinkUrl"]
            urls.append(url)

        for time, url in zip(times, urls):
            try:
                time_now = datetime.strptime(time, '%Y-%m-%d')
                self.update_last_time(time_now)
            except:
                print("Something Wrong")
                break

            if self.last_time is not None and self.last_time >= time_now:
                break

            req = scrapy.Request(url=url, callback=self.parse_info)

            m_item = DailyNewsItem()
            m_item['time'] = time
            m_item['className'] = "国际"
            # 相当于在request中加入了item这个元素
            req.meta['item'] = m_item
            yield req

    def parse_info(self, response):
        item = response.meta['item']
        item["source"] = "新华网"

        title = response.xpath('//h1[@id="title"]/text()').extract_first()
        if title is None:
            return
        item["title"] = title.strip()
        item["sourceUrl"] = response.url
        # 修改了text_list
        text_list = response.xpath('//div[@class="article"]/p')
        text = processText(text_list).strip().replace("$#$", "")
        if text == "":
            return
        item["text"] = text
        # img_list = processImgSep(text_list)
        # final_img_list = []
        # for img in img_list:
        #     if 'http' not in img:
        #         img = response.url.rsplit('/', 1)[0] + '/' + img
        #     final_img_list.append(img)
        item['imageUrls'] = None

        yield item
