#coding=utf-8
import scrapy
import re

from lad.items import LadItem
from ..spiders.beautifulSoup import processText
from datetime import datetime
from basespider import BaseTimeCheckSpider

class newsSpider(BaseTimeCheckSpider):
    name = "jiangsunew"
    start_urls = ['http://www.jsga.gov.cn/jwzx/aqff/index.html']
    text = ""

    def parse(self, response):

        should_deep = True

        times = response.xpath('//*[@width="200px"]/text()').extract()
        urls = response.xpath('/html/body/div[3]/div/div/div/div[3]/div/table/tbody/tr/td/div/a/@href').extract()
        valid_child_urls = list()

        for time, url in zip(times, urls):
            try:
                time_now = datetime.strptime(time[1:11], '%Y-%m-%d')
                self.update_last_time(time_now)
            except:
                break

            if self.last_time is not None and self.last_time >= time_now:
                should_deep = False
                break

            valid_child_urls.append("http://www.jsga.gov.cn" + url)

        next_requests = list()
        if should_deep:
            # 表示有新的url
            # 翻页
            if len(response.url) == 43:
                next_url = "http://www.jsga.gov.cn/jwzx/aqff/index_2.html"
            else:
                num = int(response.url.split('index')[1][1])
                next_url_part = "index_" + str(num + 1) + ".html"
                next_url = "http://www.jsga.gov.cn/jwzx/aqff/" + next_url_part
            yield scrapy.Request(url=next_url, callback=self.parse)
            next_requests.append(scrapy.Request(url=next_url, callback=self.parse))

        for index, temp_url in enumerate(valid_child_urls):
            req = scrapy.Request(url=temp_url, callback=self.parse_info)

            hit_time = times[index]
            m_item = LadItem()
            m_item['time'] = hit_time
            # 相当于在request中加入了item这个元素
            req.meta['item'] = m_item
            next_requests.append(req)

        for req in next_requests:
            yield req

    def parse_info(self, response):
        item = response.meta['item']

        item["city"] = "江苏"
        item["newsType"] = "警事要闻"
        item["title"] = response.xpath('//*[@id="ArticleCnt"]/div[1]/p[3]/span/text()').extract_first()
        item["time"] = response.xpath('/html/body/div[3]/div/div/div/div[3]/div[1]/text()[1]').extract_first().strip()[5:15]

        text_list = response.xpath('//*[@id="ArticleCnt"]/div[1]/p[3]/span/span/span/text()')
        if len(text_list) == 0:
            text_list = response.xpath('//*[@id="ArticleCnt"]/div[1]/p[3]/span/span/text()')
        if len(text_list) == 0:
            text_list = response.xpath('//*[@id="ArticleCnt"]/div[1]/p/span/text()')
        if len(text_list) == 0:
            text_list = response.xpath('//*[@id="ArticleCnt"]/div[1]/p/text()')

        for str_slt in text_list:
            if str_slt.extract() is None:
                self.text = self.text
            else:
                self.text = self.text + str_slt.extract()
        item["text"] = self.text
        self.text = ""

        yield item
