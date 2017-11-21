#coding=utf-8
import scrapy
import re

from lad.items import LadItem
from ..spiders.beautifulSoup import processText
from datetime import datetime
from basespider import BaseTimeCheckSpider

class newsSpider(BaseTimeCheckSpider):
    name = "nanjingnew"
    start_urls = ['http://www.njga.gov.cn/www/njga/2010/zabb.htm']
    text = ""

    def parse(self, response):

        should_deep = True

        times = response.xpath('/html/body/div/table[1]/tr/td[3]/table[5]/tr/td/table/tr/td/table/tr[2]/td/table/tr/td/div/text()').extract()
        urls = response.xpath('/html/body/div/table[1]/tr/td[3]/table[5]/tr/td/table/tr/td/table/tr[2]/td/table/tr/td/div/a/@href').extract()
        valid_child_urls = list()

        for time, url in zip(times, urls):
            try:
                time_now = datetime.strptime(time, '%Y-%m-%d')
                self.update_last_time(time_now)
            except:
                break

            if self.last_time is not None and self.last_time >= time_now:
                should_deep = False
                break

            valid_child_urls.append("http://www.njga.gov.cn/www/njga/2010/" + url)

        next_requests = list()
        if should_deep:
            # 表示有新的url
            # 翻页
            if len(response.url) == 45:
                next_url = 'http://www.njga.gov.cn/www/njga/2010/zabb_p1.htm'
            else:
                num = int(response.url.split('/')[6][6])
                next_url = 'http://www.njga.gov.cn/www/njga/2010/zabb_p' + str(num + 1) + ".htm"
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

        item["city"] = "南京公安网"
        item["newsType"] = "警事要闻"
        item["sourceUrl"] = response.url
        item["title"] = response.xpath('/html/body/div/table[1]/tr/td[3]/table[5]/tr/td/table/tr/td/table/tr[2]/td/center/table[2]/tr[1]/td/div/strong/text()').extract_first().strip()
        time_leng = len(response.xpath('/html/body/div/table[1]/tr/td[3]/table[5]/tr/td/table/tr/td/table/tr[2]/td/center/table[2]/tr[2]/td/div/text()[1]').extract_first().strip().split(']')[0].strip())
        item["time"] = response.xpath('/html/body/div/table[1]/tr/td[3]/table[5]/tr/td/table/tr/td/table/tr[2]/td/center/table[2]/tr[2]/td/div/text()[1]').extract_first().strip().split(']')[0].strip()[time_leng - 10 : time_leng]
        text_list = response.xpath('/html/body/div/table[1]/tr/td[3]/table[5]/tr/td/table/tr/td/table/tr[2]/td/center/table[3]/tr/td/div/div/div/span/text()')

        for p_slt in text_list:
            if p_slt.extract() is None:
                self.text = self.text
            else:
                self.text = self.text + p_slt.extract()
        item["text"] = self.text
        self.text = ""

        yield item
