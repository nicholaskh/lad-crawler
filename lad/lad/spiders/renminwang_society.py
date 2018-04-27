#coding=utf-8
import scrapy
import re

from ..items import DailyNewsItem
from ..spiders.beautifulSoup import processText, processImgSep
from datetime import datetime
from .basespider import BaseTimeCheckSpider

class newsSpider(BaseTimeCheckSpider):
    name = "renminwang_society"
    start_urls = ['http://society.people.com.cn/GB/136657/index1.html',
                  'http://society.people.com.cn/GB/86800/index1.html',
                  'http://society.people.com.cn/GB/1062/index1.html',
                  'http://society.people.com.cn/GB/41158/index1.html']

    def parse(self, response):
        should_deep = True
        urls = response.xpath('//div[@class="p2j_list fl"]/ul/li/a/@href').extract()
        times = list()
        valid_child_urls = list()

        for url in urls:
            # 变成绝对url
            if 'http' not in url:
                url = "http://society.people.com.cn" + url
            time = time = url.rsplit('/', 3)[-3] + "-" + url.rsplit('/', 3)[-2]
            try:
                time_now = datetime.strptime(time, '%Y-%m%d')
                self.update_last_time(time_now)
                time = time_now.strftime('%Y-%m-%d')
                times.append(time)
            except:
                print("Something Wrong")
                break

            if self.last_time is not None and self.last_time >= time_now:
                should_deep = False
                break

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
            m_item['className'] = "社会"
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
        text_list = response.xpath('//div[@class="box_con"]//p')
        text = processText(text_list)
        item["text"] = text
        img_list = processImgSep(text_list)
        final_img_list = []
        for img in img_list:
            if 'http' not in img:
                img = "http://society.people.com.cn" + img
            final_img_list.append(img)
        item['imageUrls'] = final_img_list
        if text.strip().replace("$#$", "") == "":
            return

        yield item
