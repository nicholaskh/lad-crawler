#coding=utf-8
import scrapy
import re

from ..items import DailyNewsItem
from ..spiders.beautifulSoup import processText, processImgSep
from datetime import datetime
from .basespider import BaseTimeCheckSpider

class newsSpider(BaseTimeCheckSpider):
    name = "renminwang_guoji1"
    start_urls = ['http://world.people.com.cn/GB/157278/index1.html',
                  'http://world.people.com.cn/GB/1029/42354/index1.html',
                  'http://world.people.com.cn/GB/1029/42355/index1.html',
                  'http://world.people.com.cn/GB/1029/42356/index1.html',
                  'http://world.people.com.cn/GB/1029/42361/index1.html',
                  'http://world.people.com.cn/GB/1029/42359/index1.html',
                  'http://world.people.com.cn/GB/1029/42408/index1.html',
                  'http://world.people.com.cn/GB/386750/index1.html',
                  'http://world.people.com.cn/GB/57507/index1.html',
                  'http://world.people.com.cn/GB/191609/45708/index1.html',
                  'http://world.people.com.cn/GB/191609/28277/index1.html',
                  'http://world.people.com.cn/GB/191609/113008/index1.html',
                  'http://world.people.com.cn/GB/191609/8600/index1.html',
                  'http://world.people.com.cn/GB/191609/8597/index1.html',
                  'http://world.people.com.cn/GB/191609/48936/index1.html',
                  'http://world.people.com.cn/GB/191609/152601/index1.html',
                  'http://world.people.com.cn/GB/191609/105633/index1.html',
                  'http://world.people.com.cn/GB/191609/194693/index1.html',
                  'http://world.people.com.cn/GB/191609/195123/index1.html',
                  'http://world.people.com.cn/GB/191609/196066/index1.html',
                  'http://world.people.com.cn/GB/191609/241195/index1.html',
                  'http://world.people.com.cn/GB/191609/8761/index1.html',
                  'http://world.people.com.cn/GB/191609/231775/index1.html',
                  'http://world.people.com.cn/GB/191609/30204/index1.html',
                  'http://world.people.com.cn/GB/191609/77534/index1.html',
                  'http://world.people.com.cn/GB/191609/44051/index1.html',
                  'http://world.people.com.cn/GB/191609/71374/index1.html',
                  'http://world.people.com.cn/GB/191609/104201/index1.html',
                  'http://world.people.com.cn/GB/191609/194699/index1.html',
                  'http://world.people.com.cn/GB/191609/195133/index1.html',
                  'http://world.people.com.cn/GB/191609/196151/index1.html',
                  'http://world.people.com.cn/GB/191609/203113/index1.html']

    def parse(self, response):
        should_deep = True
        times = response.xpath('//div[@class="ej_bor"]/ul/li/i/text()').extract()
        #格式不规范
        urls = response.xpath('//div[@class="ej_bor"]/ul/li/a/@href').extract()
        valid_child_urls = list()

        for time, url in zip(times, urls):
            try:
                time_now = datetime.strptime(time.split(' ')[2], '%Y-%m-%d')
                self.update_last_time(time_now)
            except:
                print("Something Wrong")
                break

            if self.last_time is not None and self.last_time >= time_now:
                should_deep = False
                break
            # 变成绝对url
            if 'http' not in url:
                url = "http://world.people.com.cn" + url
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
            m_item['time'] = hit_time.split(' ')[2]
            m_item['className'] = "国际"
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
                img = "http://world.people.com.cn" + img
            final_img_list.append(img)
        item['imageUrls'] = final_img_list
        if text.strip().replace("$#$", "") == "":
            return

        yield item
