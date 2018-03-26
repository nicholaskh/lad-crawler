#coding=utf-8
import scrapy
import re

from ..items import LadItem
from ..spiders.beautifulSoup import processText, processImgSep
from datetime import datetime
from .basespider import BaseTimeCheckSpider

class newsSpider(BaseTimeCheckSpider):
    name = "haikou_new"
    start_urls = ['http://police.haikou.gov.cn/ycjx/']

    def parse(self, response):
        should_deep = True
        times = response.xpath('//td[@class="artlist"]//tr/td[3]/text()').extract()
        #相对链接
        urls = response.xpath('//td[@class="artlist"]//tr/td[2]/a/@href').extract()

        valid_child_urls = list()

        for time, url in zip(times, urls):
            try:
                time_now = datetime.strptime(time, '%Y-%m-%d')
                self.update_last_time(time_now)
            except:
                print("Something Wrong")
                break

            if self.last_time is not None and self.last_time >= time_now:
                should_deep = False
                break
            url = "http://police.haikou.gov.cn/ycjx" + url.strip('.')
            valid_child_urls.append(url)

        next_requests = list()
        if should_deep:
            page_num = response.url.rsplit('/', 1)[-1]
            if page_num == "":
                next_url = "http://police.haikou.gov.cn/ycjx/index_1.htm"
                next_requests.append(scrapy.Request(url=next_url, callback=self.parse))
            else:
                next_page = int(page_num.split('_')[-1].split('.')[0]) + 1
                next_url = "http://police.haikou.gov.cn/ycjx/" + "index_" + str(next_page) + ".htm"
                next_requests.append(scrapy.Request(url=next_url, callback=self.parse))

        for index, temp_url in enumerate(valid_child_urls):
            req = scrapy.Request(url=temp_url, callback=self.parse_info)

            hit_time = times[index]
            m_item = LadItem()
            m_item['time'] = hit_time
            m_item['newsType'] = "警事要闻"
            # 相当于在request中加入了item这个元素
            req.meta['item'] = m_item
            next_requests.append(req)

        for req in next_requests:
            yield req

    def parse_info(self, response):
        item = response.meta['item']

        item["city"] = "海口公安网"
        title = response.xpath('//span[@class="STYLE01"]/text()').extract_first()
        if title is None:
            return
        item["title"] = title
        item["sourceUrl"] = response.url
        # 修改了text_list
        text_list = response.xpath('//div[@class="Custom_UnionStyle"]/*')
        if len(text_list) == 0:
            text_list = response.xpath('//div[@class="TRS_Editor"]/text() | //div[@class="TRS_Editor"]/*')
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
