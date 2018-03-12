#coding=utf-8
import scrapy
import re

from ..items import LadItem
from ..spiders.beautifulSoup import processText, processImgSep
from datetime import datetime
from .basespider import BaseTimeCheckSpider

class newsSpider(BaseTimeCheckSpider):
    name = "hangzhou_new"
    dict_commens = {
        '10054&page=1': '警事要闻',
        '10099&page=1': '防骗',
        '10100&page=1': '防抢',
        '10101&page=1': '交通安全',
        '10102&page=1': '防盗',
        '10103&page=1': '防火'
    }
    start_urls = ['http://www.hzpolice.gov.cn/news/morelist.aspx?moduleid=%s' % x for x in dict_commens.keys()]

    def parse(self, response):
        should_deep = True
        times = response.xpath('//div[@class="lb_right_time"]/text()').extract()
        #是相对链接
        urls = response.xpath('//div[@class="lb_right_bd"]/a/@href').extract()

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
            # 变成绝对url
            url = 'http://www.hzpolice.gov.cn' + url
            valid_child_urls.append(url)

        next_requests = list()
        if should_deep:
            page_num = int(response.url.split('&')[-1].split('=')[-1])
            real_page = int(response.xpath('//input[@name="dd_currentPage"]/@value').extract_first())
            #避免进入多余的页
            if real_page != page_num:
                return
            page_num = page_num + 1
            next_url = response.url.split('&')[0] + "&page=" + str(page_num)
            next_requests.append(scrapy.Request(url=next_url, callback=self.parse))

        for index, temp_url in enumerate(valid_child_urls):
            req = scrapy.Request(url=temp_url, callback=self.parse_info)

            hit_time = times[index]
            m_item = LadItem()
            m_item['time'] = hit_time.strip()
            key_word = response.url.split('&')[0].split('=')[-1] + "&page=1"
            news_type = self.dict_commens[key_word]
            m_item['newsType'] = news_type
            # 相当于在request中加入了item这个元素
            req.meta['item'] = m_item
            next_requests.append(req)

        for req in next_requests:
            yield req

    def parse_info(self, response):
        item = response.meta['item']

        item["city"] = "杭州公安网"
        item["title"] = response.xpath('//div[@class="nr_title"]/text()').extract_first().strip()
        item["sourceUrl"] = response.url
        # 修改了text_list
        text_list = response.xpath('//div[@class="nr_nr"][1]/*')
        text = processText(text_list)
        item["text"] = text
        img_list = processImgSep(text_list)
        final_img_list = []
        for img in img_list:
            if 'http' not in img:
                img = 'http://www.hzpolice.gov.cn' + img
            final_img_list.append(img)
        item['imageUrls'] = final_img_list
        if text.strip() == "" and len(img_list) == 0:
            return

        yield item
