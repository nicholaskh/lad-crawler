#coding=utf-8
import scrapy
import re

from ..items import DailyNewsItem
from ..spiders.beautifulSoup import processText, processImgSep
from datetime import datetime
from .basespider import BaseTimeCheckSpider

class newsSpider(BaseTimeCheckSpider):
    name = "renminwang_military"
    start_urls = ['http://military.people.com.cn/GB/172467/index1.html',
                  'http://military.people.com.cn/GB/52963/index1.html',
                  'http://military.people.com.cn/GB/115150/index1.html',
                  'http://military.people.com.cn/GB/52936/index1.html',
                  'http://military.people.com.cn/GB/367527/index1.html',
                  'http://military.people.com.cn/GB/1077/index1.html',
                  'http://military.people.com.cn/GB/367619/index1.html']

    def parse(self, response):
        should_deep = True
        times = response.xpath('//div[@class="ej_list_box clear"]/ul/li/em/text()').extract()
        #格式不规范
        urls = response.xpath('//div[@class="ej_list_box clear"]/ul/li/a/@href').extract()
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
            # 变成绝对url
            if 'http' not in url:
                url = "http://military.people.com.cn" + url
            valid_child_urls.append(url)

        next_requests = list()
        if should_deep:
            current_page = int(response.url.rsplit('.', 1)[0].rsplit('x', 1)[1])
            next_url = response.url.rsplit('/', 1)[0] + "/index" + str(current_page + 1) + ".html"
            next_requests.append(scrapy.Request(url=next_url, callback=self.parse))

        for index, temp_url in enumerate(valid_child_urls):
            req = scrapy.Request(url=temp_url, callback=self.parse_info)

            hit_time = times[index]
            m_item = DailyNewsItem()
            m_item['time'] = hit_time
            m_item['className'] = "军事"
            # 相当于在request中加入了item这个元素
            req.meta['item'] = m_item
            next_requests.append(req)

        for req in next_requests:
            yield req

    def parse_info(self, response):
        item = response.meta['item']
        item["source"] = "人民网"

        title = response.xpath('//div[@class="clearfix w1000_320 text_title"]/h1/text()').extract_first()
        if title is None:
            return
        item["title"] = title
        item["sourceUrl"] = response.url
        # 修改了text_list
        text_list = response.xpath('//div[@class="box_con"]//p | //div[@class="box_con"]//img')
        text = processText(text_list)
        item["text"] = text
        img_list = processImgSep(text_list)
        final_img_list = []
        for img in img_list:
            if 'http' not in img:
                img = "http://military.people.com.cn" + img
            final_img_list.append(img)
        item['imageUrls'] = final_img_list
        if text.strip().replace("$#$", "") == "":
            return

        yield item
