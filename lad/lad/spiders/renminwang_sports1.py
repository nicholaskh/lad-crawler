#coding=utf-8
import scrapy
import re

from ..items import DailyNewsItem
from ..spiders.beautifulSoup import processText, processImgSep
from datetime import datetime
from .basespider import BaseTimeCheckSpider

class newsSpider(BaseTimeCheckSpider):
    name = "renminwang_sports1"
    start_urls = ['http://sports.people.com.cn/GB/22155/index1.html',
                  'http://qipai.people.com.cn/GB/408735/index.html',
                  'http://qipai.people.com.cn/GB/408691/index1.html',
                  'http://qipai.people.com.cn/GB/408695/index1.html',
                  'http://qipai.people.com.cn/GB/47625/index1.html',
                  'http://qipai.people.com.cn/GB/47627/index1.html',
                  'http://qipai.people.com.cn/GB/47626/index1.html',
                  'http://sports.people.com.cn/GB/401891/401892/index1.html',
                  'http://sports.people.com.cn/jianshen/index.html',
                  'http://sports.people.com.cn/GB/22134/index1.html',
                  'http://sports.people.com.cn/GB/22141/index1.html',
                  'http://sports.people.com.cn/GB/22149/index1.html']

    def parse(self, response):
        should_deep = True
        urls = response.xpath('//div[@class="hdNews clearfix"]/p/strong/a/@href').extract()
        times = list()
        valid_child_urls = list()

        for url in urls:
            # 变成绝对url
            if 'http' not in url:
                url = "http://sports.people.com.cn" + url
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
        if should_deep and response.url.rsplit('/', 1)[1].split('.')[0] != "index":
            current_page = int(response.url.rsplit('.', 1)[0].rsplit('x', 1)[1])
            next_url = response.url.rsplit('/', 1)[0] + "/index" + str(current_page + 1) + ".html"
            next_requests.append(scrapy.Request(url=next_url, callback=self.parse))

        for index, temp_url in enumerate(valid_child_urls):
            req = scrapy.Request(url=temp_url, callback=self.parse_info)

            hit_time = times[index]
            m_item = DailyNewsItem()
            m_item['time'] = hit_time
            m_item['className'] = "体育"
            # 相当于在request中加入了item这个元素
            req.meta['item'] = m_item
            next_requests.append(req)

        for req in next_requests:
            yield req

    def parse_info(self, response):
        item = response.meta['item']
        item["source"] = "人民网"

        title = response.xpath('//div[@class="clearfix w1000_320 text_title"]/h1/text() | //div[@class="clearfix w1000 text_title"]/h1/text()').extract_first()
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
                img = "http://sports.people.com.cn" + img
            final_img_list.append(img)
        item['imageUrls'] = final_img_list
        if text.strip().replace("$#$", "") == "":
            return

        yield item
