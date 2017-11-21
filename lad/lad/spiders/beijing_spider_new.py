#coding=utf-8
import scrapy
import re

from lad.items import LadItem
from ..spiders.beautifulSoup import processText
from datetime import datetime
from basespider import BaseTimeCheckSpider

class newsSpider(BaseTimeCheckSpider):
    name = "beijingnew"
    start_urls = ['http://www.bjgaj.gov.cn/web/xwpd_zfts.html']
    text = ""

    def parse(self, response):

        should_deep = True

        times = response.xpath('//*[@id="yun1"]/tr/td/text()[2]').extract()[1:]
        urls = response.xpath('//*[@id="yun1"]/tr/td/a/@href').extract()

        valid_child_urls = list()

        for time, url in zip(times, urls):
            try:
                time_now = datetime.strptime(time[3:13], '%Y-%m-%d')
                self.update_last_time(time_now)
            except:
                break

            if self.last_time is not None and self.last_time >= time_now:
                should_deep = False
                break

            valid_child_urls.append("http://www.bjgaj.gov.cn" + url)

        next_requests = list()
        if should_deep:
            # 表示有新的url
            # 翻页
            if len(response.url) <= 42:
                next_url = 'http://www.bjgaj.gov.cn/web/listPage_allJfts_col1167_30_2.html'
            else:
                num = int(response.url[56])
                next_url = response.url[0:56] + str(num + 1) + ".html"
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

        item["city"] = "北京公安网"
        item["newsType"] = '警事要闻'
        item["title"] = response.xpath('/html/body/table[3]/tr/td/table[2]/tr/td[3]/table/tr/td/table/tr[2]/td/table/tr[1]/td/font/b/text()').extract_first()
        c = response.xpath('/html/body/table[3]/tr/td/table[2]/tr/td[3]/table/tr/td/table/tr[2]/td/table/tr[2]/td/text()').extract_first().split('www.bjgaj.gov.cn')[1].strip()
        c = re.sub("\D", "", c)
        item["time"] = c[0:4] + '-' + c[4:6] + '-' + c[6:8]

        text_list = response.xpath('//*[@id="articleContent"]/p')

        for p_slt in text_list:
            if p_slt.xpath('text()').extract_first() is None:
                self.text = self.text
            else:
                self.text = self.text + p_slt.xpath('text()').extract_first()
        item["text"] = self.text
        self.text = ""

        yield item
