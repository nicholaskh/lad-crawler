#coding=utf-8
import scrapy
import re

from ..items import LadItem
from ..spiders.beautifulSoup import processText, processImgSep
from datetime import datetime
from .basespider import BaseTimeCheckSpider

class newsSpider(BaseTimeCheckSpider):
    name = "shanghaigongan"
    start_urls = ['http://www.police.sh.cn/shga/wzXxfbGj/getList?pa=f41aa3d5accbfad14fcbf784730c1c7fd590f9edd6394372&page=1']

    def parse(self, response):
        should_deep = True
        times = response.xpath('//*[@id="neiy_center"]/div[2]//em/text()').extract()
        #是相对链接
        urls_ori = response.xpath('//*[@id="neiy_center"]/div[2]//a/@href').extract()
        urls = []
        for each in urls_ori:
            url = 'http://www.police.sh.cn/shga/wzXxfbGj/detail?pa=' + each[18:-2]
            urls.append(url)

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
            #url = 'http://www.hzpolice.gov.cn' + url
            valid_child_urls.append(url)

        next_requests = list()
        if should_deep:
            if len(times) != 0:
                currentPageNum = int(response.url.split('=')[-1])
                nextPageNum = currentPageNum + 1
                next_url = 'http://www.police.sh.cn/shga/wzXxfbGj/getList?pa=f41aa3d5accbfad14fcbf784730c1c7fd590f9edd6394372&page=' + str(nextPageNum)
                req = scrapy.Request(url=next_url, callback=self.parse)
                yield req

        for index, temp_url in enumerate(valid_child_urls):
            req = scrapy.Request(url=temp_url, callback=self.parse_info)
            m_item = LadItem()
            m_item['time'] = times[index]
            m_item['newsType'] = "警事要闻"
            req.meta['item'] = m_item
            yield req

    def parse_info(self, response):
        item = response.meta['item']

        item["city"] = "上海公安网"
        item["title"] = response.xpath('//*[@id="ivs_title"]/text()').extract()[0]
        item["sourceUrl"] = response.url
        # 修改了text_list
        #text_list = response.xpath('//*[@id="ivs_content"]/p/text() | //*[@id="ivs_content"]/p//font/text()')
        text_list = response.xpath('//*[@id="ivs_content"]/* | //*[@id="gjnr"]/div[1]/*')
        text = processText(text_list)
        item["text"] = text

        text_list = response.xpath('//*[@id="ivs_content"]/* | //*[@id="gjnr"]/div[1]/*')
        img_list = processImgSep(text_list)
        final_img_list = []
        for img in img_list:
            if 'http' not in img:
                img = '' + img
            final_img_list.append(img)
        item['imageUrls'] = final_img_list
        if text.strip() == "" and len(img_list) == 0:
            return

        yield item
