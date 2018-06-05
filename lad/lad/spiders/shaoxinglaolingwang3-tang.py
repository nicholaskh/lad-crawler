#coding=utf-8
import scrapy
import re

from ..items import YanglaoItem
from ..spiders.beautifulSoup import processText, processImgSep
from datetime import datetime
from .basespider import BaseTimeCheckSpider

class newsSpider(BaseTimeCheckSpider):
    name = "shaoxinglaolingwang3"
    start_urls = ['http://sx60.sx.gov.cn/col/col493/index.html']

    def parse(self, response):
        should_deep = True

        times_ori = response.xpath('//*[@id="6351"]/div//td/text()').extract()
        if len(times_ori) == 0:
            should_deep =False
        times = []
        for each in times_ori:
            times.append(each[1:-1])

        #是相对链接
        urls_ori = response.xpath('//*[@id="6351"]/div//a/@href').extract()
        urls = []
        for each in urls_ori:
            each = 'http://sx60.sx.gov.cn' + each
            urls.append(each)

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
            #url = 'http://www.hebllw.org.cn' + url
            valid_child_urls.append(url)

        next_requests = list()
        # if should_deep:
        #     #maxPageNum = int(response.xpath('//div[@class="pagenum_label"]//dd/p/text()').extract()[0].strip())
        #     if '_' in response.url:
        #         currentPageNum =int(response.url.split('_')[-1].split('.')[0])
        #     else:
        #         currentPageNum = 0
        #
        #     nextPageNum = currentPageNum + 1
        #     if nextPageNum > 10:
        #         return
        #
        #     next_url = 'http://llw.lishui.gov.cn/llgz/gzzx/index_' + str(nextPageNum) + '.htm'
        #     req = scrapy.Request(url=next_url, callback=self.parse)
        #     yield req

        for index, temp_url in enumerate(valid_child_urls):
            req = scrapy.Request(url=temp_url, callback=self.parse_info)
            m_item = YanglaoItem()
            #m_item['title'] = titles[index]
            m_item['time'] = times[index]
            m_item['className'] = '老龄新闻'
            req.meta['item'] = m_item
            yield req

    def parse_info(self, response):
        item = response.meta['item']

        item["source"] = "绍兴老龄网"

        # title_ori =  response.xpath('//div[@class="w96"]/h1/text() | //div[@class="w96"]/h1/span/text()').extract()
        # title =''
        # for each in title_ori:
        #     title = title + each
        item["title"] = response.xpath('//td[@align="center"]/text()').extract()[1]

        item["sourceUrl"] = response.url
        # 修改了text_list
        #text_list = response.xpath('//*[@id="ivs_content"]/p/text() | //*[@id="ivs_content"]/p//font/text()')
        text_list = response.xpath('//div[@id="zoom"]/*')
        text = processText(text_list)
        item["text"] = text

        text_list = response.xpath('//div[@id="zoom"]/*')
        img_list = processImgSep(text_list)
        final_img_list = []
        for img in img_list:
            if 'http' not in img:
                img = 'http://sx60.sx.gov.cn' + img
            final_img_list.append(img)
        item['imageUrls'] = final_img_list
        if text.strip() == "" and len(img_list) == 0:
            return

        yield item
