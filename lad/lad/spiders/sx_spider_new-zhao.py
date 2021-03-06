#coding=utf-8
import scrapy
import re

from ..items import LadItem
from ..spiders.beautifulSoup import processText, processImgSep
from datetime import datetime
from .basespider import BaseTimeCheckSpider

class newsSpider(BaseTimeCheckSpider):
    name = "sx_new"
    start_urls = ['http://site.sxgabmfw.gov.cn/site/public/techlist.aspx?menuid=400606&page=1']

    def parse(self, response):
        should_deep = True
        times = response.xpath('//div[@id="list1"]/ul/li/font/text()').extract()
        #相对链接
        urls = response.xpath('//div[@id="list1"]/ul/li/a/@href').extract()

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
            url = "http://site.sxgabmfw.gov.cn/site/public/" + url
            valid_child_urls.append(url)

        next_requests = list()
        if should_deep:
            page_num = int(response.url.rsplit('=', 1)[-1])
            current_page = response.xpath('//span[@class="cpb"]/text()').extract_first()
            if current_page is not None and int(current_page) == page_num:
                next_page = page_num + 1
                next_url = response.url.rsplit('=', 1)[0] + "=" + str(next_page)
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

        item["city"] = "山西公安网"
        title = response.xpath('//span[@id="defaultmain_title"]/text()').extract_first()
        if title is None:
            return
        item["title"] = title
        item["sourceUrl"] = response.url
        # 修改了text_list
        text_list = response.xpath('//span[@id="defaultmain_content"]/*')
        text = processText(text_list)
        item["text"] = text
        img_list = processImgSep(text_list)
        final_img_list = []
        for img in img_list:
            if 'http' not in img:
                img = "http://site.sxgabmfw.gov.cn" + img
            final_img_list.append(img)
        item['imageUrls'] = final_img_list
        if text.strip() == "" and len(img_list) == 0:
            return

        yield item
