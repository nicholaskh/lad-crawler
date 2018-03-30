#coding=utf-8
import scrapy
import re

from ..items import LadItem
from ..spiders.beautifulSoup import processText, processImgSep
from datetime import datetime
from .basespider import BaseTimeCheckSpider

class newsSpider(BaseTimeCheckSpider):
    name = "liaoninggongan"
    start_urls = ['http://www.lnga.gov.cn/jwzx/jfts/index.html']

    def parse(self, response):
        should_deep = True
        times_ori = response.xpath('//*[@id="left"]/div[2]//span/text()').extract()
        times = []
        for each in times_ori:
            if '-' in each:
                times.append(each)

        #是相对链接
        urls_ori =  response.xpath('//*[@id="left"]/div[2]//a/@href').extract()
        urls = []
        for each in urls_ori:
            url = 'http://www.lnga.gov.cn/jwzx/jfts' + each[1:]
            urls.append(url)

        #titles = response.xpath('/html/body/div[3]/div/div/div/div[3]/div/table/tbody//a/text()').extract()

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
        # #if should_deep:
        #     #maxPageNum = int(response.xpath('//*[@id="pre"]/a/@href').extract()[-1].split('_')[-1].split('.')[0])
        #     #if '_' not in response.url:
        #         currentPageNum = 0
        #     else:
        #         currentPageNum = int(response.url.split('_')[-1].split('.')[0])
        #
        #     nextPageNum = currentPageNum + 1
        #     next_url = 'http://www.lnga.gov.cn/jwzx/jfts/index_' + str(nextPageNum) + '.html'
        #     req = scrapy.Request(url=next_url, callback=self.parse)
        #     yield req

        for index, temp_url in enumerate(valid_child_urls):
            req = scrapy.Request(url=temp_url, callback=self.parse_info)
            m_item = LadItem()
            m_item['time'] = times[index]
            #m_item['title'] = titles[index]
            m_item['newsType'] = "警事要闻"
            req.meta['item'] = m_item
            yield req

    def parse_info(self, response):
        item = response.meta['item']
        item["city"] = "辽宁公安网"
        item["title"] = response.xpath('//*[@id="img-content"]/h2/text()').extract()[0].strip()
        item["sourceUrl"] = response.url
        # 修改了text_list
        #text_list = response.xpath('//*[@id="ivs_content"]/p/text() | //*[@id="ivs_content"]/p//font/text()')
        text_list = response.xpath('//*[@id="js_content"]//p')
        text = processText(text_list)
        item["text"] = text

        text_list = response.xpath('//*[@id="js_content"]//p')
        img_list = processImgSep(text_list)
        final_img_list = []
        # for img in img_list:
        #     if 'http' not in img:
        #         img = '' + img
        #     final_img_list.append(img)
        item['imageUrls'] = final_img_list
        if text.strip() == "" and len(img_list) == 0:
            return

        yield item
