#coding=utf-8
import scrapy
import re

from ..items import LadItem
from ..spiders.beautifulSoup import processText, processImgSep
from datetime import datetime

class newsSpider(scrapy.Spider):
    name = "hainan"
    start_urls = ['http://ga.hainan.gov.cn/28/']

    def parse(self, response):
        # should_deep = True
        times = response.xpath('//tr[@class="td_bg_RowA"]/td[3]/text()').extract()
        #相对链接
        urls = response.xpath('//tr[@class="td_bg_RowA"]/td[2]/a/@href').extract()

        for time, url in zip(times, urls):
            true_url = "http://ga.hainan.gov.cn" + url
            req = scrapy.Request(url=true_url, callback=self.parse_info)
            m_item = LadItem()
            m_item['time'] = time.strip()
            m_item['newsType'] = "警事要闻"
            # 相当于在request中加入了item这个元素
            req.meta['item'] = m_item
            yield req

    def parse_info(self, response):
        item = response.meta['item']

        item["city"] = "海南公安网"
        title = response.xpath('//font[@color]/text()').extract_first()
        if title is None:
            return
        item["title"] = title
        item["sourceUrl"] = response.url
        # 修改了text_list
        text_list = response.xpath('//div[@id="artibody"]/table/*[position()>2]')
        text = processText(text_list)
        item["text"] = text.strip()
        img_list = processImgSep(text_list)
        final_img_list = []
        for img in img_list:
            if 'http' in img:
                final_img_list.append(img)
        item['imageUrls'] = final_img_list
        if text.strip() == "" and len(img_list) == 0:
            return

        yield item
