#coding=utf-8
import scrapy
import re

from ..items import LadItem
from ..spiders.beautifulSoup import processText, processImgSep
from datetime import datetime
from .basespider import BaseTimeCheckSpider

class newsSpider(BaseTimeCheckSpider):
    name = "guangdonggongan2"
    start_urls = ['http://www.gdga.gov.cn/jwzx/jsyw/list.html']

    def parse(self, response):
        should_deep = True
        times_ori = response.xpath('//*[@id="conList"]//span/text()').extract()
        times = []
        for each in times_ori:
            part = each.split('.')
            time = part[0] + '-' + part[1] + '-' + part[2]
            times.append(time)

        #是相对链接
        urls_ori = response.xpath('//*[@id="conList"]//a/@href').extract()
        urls = []
        for each in urls_ori:
            if '../..' in each:
                url = 'http://www.gdga.gov.cn' + each[5:]
            elif '../' in each:
                url = 'http://www.gdga.gov.cn/jwzx/' + each[3:]
            else:
                url = 'http://www.gdga.gov.cn/jwzx/jsyw' + each[1:]
            urls.append(url)

        valid_child_urls = list()

        titles = response.xpath('//*[@id="conList"]//a/@title').extract()

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
            #url = 'http://www.hzpolice.gov.cn' + url
            valid_child_urls.append(url)

        next_requests = list()
        continuetocrawl = True
        if should_deep:
            if len(times_ori) == 0:
                continuetocrawl = False

            if continuetocrawl == True:
                if 'list.html' in response.url:
                    currentPageNum = 0
                else:
                    currentPageNum = int(response.url.split('_')[-1].split('.')[0])

                nextPageNum = currentPageNum + 1
                next_url = 'http://www.gdga.gov.cn/jwzx/jsyw/list_' + str(nextPageNum) + '.html'
                req = scrapy.Request(url=next_url, callback=self.parse)
                yield req

        for index, temp_url in enumerate(valid_child_urls):
            req = scrapy.Request(url=temp_url, callback=self.parse_info)
            m_item = LadItem()
            m_item['time'] = times[index]
            m_item['title'] = titles[index]
            m_item['newsType'] = "警事要闻"
            req.meta['item'] = m_item
            yield req

    def parse_info(self, response):
        item = response.meta['item']

        item["city"] = "广东公安网"
        #item["title"] = response.xpath('//*[@id="ivs_title"]/text()').extract()[0]
        item["sourceUrl"] = response.url
        # 修改了text_list
        #text_list = response.xpath('//*[@id="ivs_content"]/p/text() | //*[@id="ivs_content"]/p//font/text()')
        text_list = response.xpath('//div[@class="Custom_UnionStyle"]//p')
        if len(text_list) == 0:
            response.xpath('//div[@class="endTxt lk169"]//p')
        text = processText(text_list)
        item["text"] = text

        text_list = response.xpath('//div[@class="Custom_UnionStyle"]//p')
        if len(text_list) == 0:
            response.xpath('//div[@class="endTxt lk169"]//p')
        img_list = processImgSep(text_list)
        final_img_list = []
        img_url = 'www.gdga.gov.cn'
        for i in range(3, len(response.url.split('/')) - 1):
            img_url = img_url + '/' + response.url.split('/')[i]
        for img in img_list:
            if 'http' not in img:
                img = img_url + img[1:]
                img = 'http://' + img
            final_img_list.append(img)
        item['imageUrls'] = final_img_list
        if text.strip() == "" and len(img_list) == 0:
            return

        yield item
