#coding=utf-8
import scrapy
import re

from lad.items import LadItem
from ..spiders.beautifulSoup import processText
from datetime import datetime
from basespider import BaseTimeCheckSpider

class newsSpider(BaseTimeCheckSpider):
    name = "kunmingnew"
    start_urls = ['http://gaj.km.gov.cn/zxdt/jwdt/']
    text = ""

    def parse(self, response):

        should_deep = True

        times = response.xpath('//*[@class="lists"]/ul/li/span/text()').extract()
        urls = response.xpath('//*[@class="lists"]/ul/li/a/@href').extract()

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
            valid_child_urls.append('http://gaj.km.gov.cn' + url)

        next_requests = list()
        if should_deep:
            # 表示有新的url
            # 翻页
            if len(response.url) == 31:
                next_url = "http://gaj.km.gov.cn/zxdt/jwdt/index_2.shtml"
            else:
                part_str = response.url.split('/')[5]
                num = int(part_str[6])
                next_url_part = "index_" + str(num + 1) + ".shtml"
                next_url = response.url.split('index')[0] + next_url_part
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

        item["newsType"] = "警事要闻"
        item["title"] = response.xpath('/html/body/div[5]/div[2]/div[2]/h1/text()').extract_first()
        c = response.xpath('/html/body/div[5]/div[2]/div[2]/div[1]/span[1]/text()').extract_first()
        c = re.sub("\D", "", c)
        item["city"] = "昆明公安网"
        item["sourceUrl"] = response.url
        item["time"] = c[0:4] + '-' + c[4:6] + '-' + c[6:8]

        text_list = response.xpath('/html/body/div[5]/div[2]/div[2]/div[2]/p')

        for str_slt in text_list:
            if str_slt.xpath('text()').extract_first() is None:
                self.text = self.text
            else:
                self.text = self.text + str_slt.xpath('text()').extract_first()
        item["text"] = self.text
        self.text = ""

        yield item
