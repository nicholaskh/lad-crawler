#coding=utf-8
import scrapy
import re

from ..items import LadItem
from ..spiders.beautifulSoup import processText, processImgSep
from datetime import datetime
from .basespider import BaseTimeCheckSpider

class newsSpider(BaseTimeCheckSpider):
    name = "changchun_new"
    start_urls = ['http://www.ccga.gov.cn/ga/4/2/s2.shtml']

    def parse(self, response):
        should_deep = True
        times = response.xpath('//table[@width="95%"]//table/tr/td[3]/text()').extract()
        urls = response.xpath('//table[@width="95%"]//table/tr/td[2]/span/a/@href').extract()

        valid_child_urls = list()

        for time, url in zip(times, urls):
            try:
                time_now = datetime.strptime(time.strip(), '%Y-%m-%d')
                self.update_last_time(time_now)
            except:
                print("Something Wrong")
                break

            if self.last_time is not None and self.last_time >= time_now:
                should_deep = False
                break
            valid_child_urls.append(url)

        next_requests = list()
        if should_deep:
            if response.url.rsplit('/', 1)[-1] == "s2.shtml":
                next_url = "http://www.ccga.gov.cn/ga/4/2/s2_2.shtml"
                next_requests.append(scrapy.Request(url=next_url, callback=self.parse))
            else:
                page_num = int(response.url.rsplit('/', 1)[-1].split('_')[-1].split('.')[0])
                next_page = page_num + 1
                next_url = response.url.split('_')[0] + "_" + str(next_page) + ".shtml"
                next_requests.append(scrapy.Request(url=next_url, callback=self.parse))

        for index, temp_url in enumerate(valid_child_urls):
            req = scrapy.Request(url=temp_url, callback=self.parse_info)

            hit_time = times[index]
            m_item = LadItem()
            m_item['time'] = hit_time.strip()
            m_item['newsType'] = "警事要闻"
            # 相当于在request中加入了item这个元素
            req.meta['item'] = m_item
            next_requests.append(req)

        for req in next_requests:
            yield req

    def parse_info(self, response):
        item = response.meta['item']

        item["city"] = "长春公安网"
        item["title"] = response.xpath('//td[@width="981"]/text()').extract_first().strip()
        item["sourceUrl"] = response.url
        # 修改了text_list
        text_list = response.xpath('//div[@id="divInfoContent"]/*')
        text = processText(text_list)
        item["text"] = text
        img_list = processImgSep(text_list)
        final_img_list = []
        for img in img_list:
            if 'http' not in img:
                img = response.url.rsplit('/', 1)[0] + img.strip('.')
            final_img_list.append(img)
        item['imageUrls'] = final_img_list
        if text.strip() == "" and len(img_list) == 0:
            return

        yield item
