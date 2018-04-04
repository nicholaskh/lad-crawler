#coding=utf-8
import scrapy
import re

from ..items import DailyNewsItem
from ..spiders.beautifulSoup import processText, processImgSep
from datetime import datetime,timedelta
from .basespider import BaseTimeCheckSpider

class newsSpider(BaseTimeCheckSpider):
    name = "chinanews_2"
    dict_commens = {
        'http://www.chinanews.com/scroll-news/ty/': '体育',
        'http://www.chinanews.com/scroll-news/sh/': '社会',
        'http://www.chinanews.com/scroll-news/gj/': '国际',
        'http://www.chinanews.com/scroll-news/gn/': '政治',
        'http://www.chinanews.com/scroll-news/mil/': '军事'
    }
    url_tail = "/news.shtml"

    def start_requests(self):
        begin = datetime.now()
        self.update_last_time(begin)
        end = datetime(2015, 1, 1)
        for i in range((begin-end).days+1):
            day = begin - timedelta(days=i)
            format_day = day.strftime('%Y/%m%d')
            if self.last_time is not None and self.last_time >= day:
                break
            for name, url in zip(self.dict_commens.values(), self.dict_commens.keys()):
                true_url = url + str(format_day) + self.url_tail
                req = scrapy.Request(url=true_url, callback=self.parse)
                m_item = DailyNewsItem()
                m_item['time'] = str(day.strftime('%Y-%m-%d'))
                m_item['className'] = name
                # 相当于在request中加入了item这个元素
                req.meta['item'] = m_item
                yield req

    def parse(self, response):
        m_item = response.meta['item']
        urls = response.xpath('//div[@class="content_list"]//a/@href').extract()

        for url in urls:
            req = scrapy.Request(url=url, callback=self.parse_info)
            req.meta['item'] = m_item
            yield req

    def parse_info(self, response):
        item = response.meta['item']
        item["source"] = "中国新闻网"
        title = response.xpath('//*[@id="cont_1_1_2"]/h1/text()').extract_first()
        if title is None:
            return
        item["title"] = title.strip()
        item["sourceUrl"] = response.url
        # 修改了text_list
        text_list = response.xpath('//div[@class="left_zw"]/p')
        text = processText(text_list)
        item["text"] = text
        img_list = processImgSep(text_list)
        final_img_list = []
        for img in img_list:
            if 'http' in img:
                final_img_list.append(img)
        item['imageUrls'] = final_img_list
        if text.strip().replace("$#$", "") == "":
            return
        yield item
