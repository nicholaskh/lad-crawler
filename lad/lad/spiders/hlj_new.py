#coding=utf-8
import scrapy
import re

from ..items import LadItem
from ..spiders.beautifulSoup import processText, processImgSep
from datetime import datetime
from .basespider import BaseTimeCheckSpider

class newsSpider(BaseTimeCheckSpider):
    name = "hlj_new"
    dict_commens = {
        'jwzx/qgyw/': '警事要闻',
        'zazj/ljda/': '警事要闻',
        'zazj/qgya/': '警事要闻',
        'zazj/ywjs/': '警事要闻'
    }
    start_urls = ['http://www.hljga.gov.cn/%s' % x for x in dict_commens.keys()]

    def parse(self, response):
        should_deep = True
        times = response.xpath('//div[@class="gawxr-lie"]//li/span/text()').extract()
        #是相对链接
        urls = response.xpath('//div[@class="gawxr-lie"]//li/a/@href').extract()

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
            url = 'http://www.hljga.gov.cn' + url
            valid_child_urls.append(url)

        next_requests = list()
        if should_deep:
            if response.url.rsplit('/', 1)[-1] == "":
                next_url = response.url.rsplit('/', 3)[0] + "/system/more/" + response.url.rsplit('/', 3)[1] + "/" \
                           + response.url.rsplit('/', 3)[2] + "/index/page_" + "01.html"
                next_requests.append(scrapy.Request(url=next_url, callback=self.parse))
            else:
                page_num = int(response.url.rsplit('/', 1)[-1].split('_')[-1].split('.')[0])
                next_page = page_num + 1
                next_url = response.url.split('_')[0] + "_" + str(next_page).zfill(2) + ".html"
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

        item["city"] = "黑龙江公安网"
        item["title"] = response.xpath('//div[@class="tm2"]/text()').extract_first().strip()
        item["sourceUrl"] = response.url
        # 修改了text_list
        text_list = response.xpath('//div[@class="nr5"]/*')
        text = processText(text_list)
        item["text"] = text
        img_list = processImgSep(text_list)
        # final_img_list = []
        # for img in img_list:
        #     if 'http' not in img:
        #         img = 'http://www.hzpolice.gov.cn' + img
        #     final_img_list.append(img)
        item['imageUrls'] = img_list
        if text.strip() == "" and len(img_list) == 0:
            return

        yield item
