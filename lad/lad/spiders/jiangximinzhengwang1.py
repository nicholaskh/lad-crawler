#coding=utf-8
import scrapy
import re

from ..items import YanglaoItem
from ..spiders.beautifulSoup import processText, processImgSep
from datetime import datetime
from .basespider import BaseTimeCheckSpider

class newsSpider(BaseTimeCheckSpider):
    name = "jiangximinzhengwang1"
    start_urls = ['http://www.jxmzw.gov.cn/llb/zcfg/index.shtml']

    def parse(self, response):
        should_deep = True

        times = response.xpath('//div[@class="mztcen"]//div[@class="news_lb"]/span/text()').extract()
        if len(times) == 0:
            should_deep =False

        #是相对链接
        urls = response.xpath('//div[@class="mztcen"]//div[@class="news_lb"]/p/a/@href').extract()

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
        #     maxPageNum = int(response.xpath('//div[@class="pagenum_label"]//dd/p/text()').extract()[0].strip())
        #     if 'index' in response.url:
        #         currentPageNum = 1
        #     else:
        #         currentPageNum = int(response.url.split('/')[-1].split('.')[0])
        #
        #     nextPageNum = currentPageNum + 1
        #     if nextPageNum > 10:
        #         return
        #
        #     next_url = 'http://www.hbllw.cn/html/xwzx/gnzx/' + str(nextPageNum) + '.html'
        #     req = scrapy.Request(url=next_url, callback=self.parse)
        #     yield req

        for index, temp_url in enumerate(valid_child_urls):
            req = scrapy.Request(url=temp_url, callback=self.parse_info)
            m_item = YanglaoItem()
            #m_item['title'] = titles[index]
            m_item['time'] = times[index]
            m_item['className'] = '政策法规'
            req.meta['item'] = m_item
            yield req

    def parse_info(self, response):
        item = response.meta['item']

        item["source"] = "江西民政网"

        # title_ori =  response.xpath('//div[@class="w96"]/h1/text() | //div[@class="w96"]/h1/span/text()').extract()
        # title =''
        # for each in title_ori:
        #     title = title + each
        item["title"] = response.xpath('//div[@class="mzt_title"]/h2/text()').extract()[0]

        item["sourceUrl"] = response.url
        # 修改了text_list
        #text_list = response.xpath('//*[@id="ivs_content"]/p/text() | //*[@id="ivs_content"]/p//font/text()')
        text_list = response.xpath('//div[@class="wz_contect"]//p')
        text = processText(text_list)
        item["text"] = text

        text_list = response.xpath('//div[@class="wz_contect"]//p')
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
