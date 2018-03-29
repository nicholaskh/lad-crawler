#coding=utf-8
import scrapy
import re

from ..items import LadItem
from ..spiders.beautifulSoup import processText, processImgSep
from datetime import datetime
from .basespider import BaseTimeCheckSpider

class newsSpider(BaseTimeCheckSpider):
    name = "beijinggongan2"
    start_urls = ['http://www.bjgaj.gov.cn/web/listPage_getArticlesByJftsClass_2c94eca7194bd75901194be522b1000f_col1167_30_1.html']

    def parse(self, response):
        should_deep = True
        times_ori = response.xpath('//td[@valign="top"]//td/text()').extract()
        times = []
        for each in times_ori:
            time = re.findall(r'(\d\d\d\d-\d\d-\d\d)', each)
            if len(time) != 0:
                times.append(time[0])

        #是相对链接
        urls_ori = response.xpath('//td[@valign="top"]//a/@href').extract()
        urls = []
        for each in urls_ori:
            if '/web/detail_getArticleInfo_' in each:
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
            url = 'http://www.bjgaj.gov.cn' + url
            valid_child_urls.append(url)

        next_requests = list()
        if should_deep:
            maxPageNum = int(re.findall(u'找到(.*?)条记录, 共(.*?)页', response.xpath('//tr[@align="center"]').extract()[1])[0][1])
            current_pagenum = int(response.url.split('_')[-1].split('.')[0])
            if current_pagenum < maxPageNum:
                next_pagenum = str(current_pagenum + 1)
                next_url = 'http://www.bjgaj.gov.cn/web/listPage_getArticlesByJftsClass_2c94eca7194bd75901194be522b1000f_col1167_30_' + next_pagenum + '.html'
                req = scrapy.Request(url=next_url, callback=self.parse)
                yield req

        for index, temp_url in enumerate(valid_child_urls):
            req = scrapy.Request(url=temp_url, callback=self.parse_info)
            m_item = LadItem()
            m_item['time'] = times[index]
            m_item['newsType'] = "防火"
            req.meta['item'] = m_item
            yield req

    def parse_info(self, response):
        item = response.meta['item']

        item["city"] = "北京市公安局"
        item["title"] = response.xpath('//font[@size="3"]/b/text()').extract()[0]
        item["sourceUrl"] = response.url
        # 修改了text_list
        text_list = response.xpath('//td[@colspan="2"]/div/*')
        text = processText(text_list)
        item["text"] = text
        img_list = processImgSep(text_list)
        final_img_list = []
        for img in img_list:
            if 'http' not in img:
                img = 'http://www.bjgaj.gov.cn' + img
            final_img_list.append(img)
        item['imageUrls'] = final_img_list
        if text.strip() == "" and len(img_list) == 0:
            return

        yield item
