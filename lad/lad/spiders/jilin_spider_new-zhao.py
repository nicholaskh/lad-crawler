#coding=utf-8
import scrapy
import re

from ..items import LadItem
from ..spiders.beautifulSoup import processText, processImgSep
from datetime import datetime
from .basespider import BaseTimeCheckSpider

class newsSpider(BaseTimeCheckSpider):
    name = "jilin_new"
    dict_commens = {
        'aqff/': '警事要闻',
        'wzzj/': '警事要闻',
        'jfts/': '警事要闻'
    }
    start_urls = ['http://gat.jl.gov.cn/jmhd/%s' % x for x in dict_commens.keys()]

    def parse(self, response):
        should_deep = True
        times = response.xpath('//table[@width="99%"]/tr/td[2]/text()').extract()
        #是相对链接
        urls = response.xpath('//table[@width="99%"]/tr/td[1]/a/@href').extract()
        valid_child_urls = list()

        for time, url in zip(times, urls):
            try:
                time_now = datetime.strptime(time.strip('[').strip(']'), '%Y-%m-%d')
                self.update_last_time(time_now)
            except:
                print("Something Wrong")
                break

            if self.last_time is not None and self.last_time >= time_now:
                should_deep = False
                break
            # 变成绝对url
            url = response.url.rsplit('/', 1)[0] + url.strip('.')
            valid_child_urls.append(url)

        next_requests = list()
        if should_deep:
            currentPage = int(re.findall('var currentPage = (.*?);', response.text)[0])
            pageCount = int(re.findall('var countPage = (.*?)/', response.text)[0])
            if currentPage < pageCount-1:
                next_url = response.url.rsplit('/', 1)[0] + "/index_" + str(currentPage + 1) + ".html"
                next_requests.append(scrapy.Request(url=next_url, callback=self.parse))

        for index, temp_url in enumerate(valid_child_urls):
            req = scrapy.Request(url=temp_url, callback=self.parse_info)

            hit_time = times[index]
            m_item = LadItem()
            m_item['time'] = hit_time.strip('[').strip(']')
            key_word = response.url.rsplit('/', 2)[1] + "/"
            news_type = self.dict_commens[key_word]
            m_item['newsType'] = news_type
            # 相当于在request中加入了item这个元素
            req.meta['item'] = m_item
            next_requests.append(req)

        for req in next_requests:
            yield req

    def parse_info(self, response):
        item = response.meta['item']

        item["city"] = "吉林公安网"
        item["title"] = response.xpath('//td[@class="red_tit"]/text()').extract_first()
        item["sourceUrl"] = response.url
        # 修改了text_list
        text_list = response.xpath('//div[@class="TRS_Editor"]/text() | '
                                   '//div[@class="TRS_Editor"]/text() | '
                                   '//div[@class="Custom_UnionStyle"]/* ')
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
