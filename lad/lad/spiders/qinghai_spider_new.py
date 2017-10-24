#coding=utf-8
import scrapy
import re

from lad.items import LadItem
from ..spiders.beautifulSoup import processText
from datetime import datetime
from basespider import BaseTimeCheckSpider

class newsSpider(BaseTimeCheckSpider):
    name = "qinghainew"
    districts = ['Category_115', 'Category_111']
    start_urls = ['http://www.qhga.gov.cn/%s/Index.aspx' % x for x in districts]
    text = ""

    def parse(self, response):

        should_deep = True

        times = response.xpath('//*[@class="article_list"]/li/span/text()').extract()
        urls = response.xpath('//*[@class="article_list"]/li/a/@href').extract()

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

            valid_child_urls.append("http://www.qhga.gov.cn" + url)

        next_requests = list()

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

        item["city"] = "青海"
        item["newsType"] = '警事要闻'
        item["title"] = response.xpath('/html/body/div/div[2]/div[2]/h1/text()').extract_first()
        c = response.xpath('/html/body/div/div[2]/div[2]/div[1]/span[4]/text()').extract_first()[5:16]
        c = re.sub("\D", "", c)
        item["time"] = c[0:4] + '-' + c[4:6] + '-' + c[6:8]

        text_list = response.xpath('//*[@id="fontzoom"]/p/span')

        if len(text_list) >= 2:
            for str_slt in text_list:
                if str_slt.xpath('text()').extract_first() is None:
                    self.text = self.text
                else:
                    self.text = self.text + str_slt.xpath('text()').extract_first()
            item["text"] = self.text
        else:
            if text_list.xpath('text()').extract_first() is None:
                self.text = self.text
            else:
                self.text = self.text + text_list.xpath('text()').extract_first()
        self.text = ""

        yield item
