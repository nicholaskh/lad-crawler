#coding=utf-8
import scrapy
import re

from ..items import LadItem
from ..spiders.beautifulSoup import processText, processImgSep
from datetime import datetime
from .basespider import BaseTimeCheckSpider

class newsSpider(BaseTimeCheckSpider):
    name = "guangzhougongan"
    start_urls = ['http://www.gzjd.gov.cn/gzjdw/gaxw/ztbd/ffzp/list-1.shtml']

    def parse(self, response):
        should_deep = True
        times_ori = response.xpath('/html/body/div[2]/section/div/div[2]/div[2]/ul//span/text()').extract()
        times = []
        for each in times_ori:
            temp = re.findall(r'(\d\d\d\d)-(.*?)-(\d{1,2})',times_ori[0])[0]
            time = temp[0] + '-' + temp[1] + '-' + temp[2]
            times.append(time)

        #是相对链接
        urls_ori = list(set(response.xpath('/html/body/div[2]/section/div/div[2]/div[2]/ul//a/@href').extract()))
        urls = []
        for each in urls_ori:
            url = 'http://www.gzjd.gov.cn' + each
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
            maxPageNum = int(response.xpath('//div[@class="pagenum_label"]//dd/p/text()').extract()[0].strip())
            currentPageNum = int(response.url.split('-')[-1].split('.')[0])
            if currentPageNum < maxPageNum:
                nextPageNum = currentPageNum + 1
                next_url = 'http://www.gzjd.gov.cn/gzjdw/gaxw/ztbd/ffzp/list-' + str(nextPageNum) + '.shtml'
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

        item["city"] = "广州公安网"
        item["title"] = response.xpath('//dt[@class="f_22 fc_2d"]/text()').extract()[0].strip()
        item["sourceUrl"] = response.url
        # 修改了text_list
        #text_list = response.xpath('//*[@id="ivs_content"]/p/text() | //*[@id="ivs_content"]/p//font/text()')
        text_list = response.xpath('//div[@class="news_content_txt2"]/*')
        text = processText(text_list)
        item["text"] = text

        text_list = response.xpath('//div[@class="news_content_txt2"]/*')
        img_list = processImgSep(text_list)
        final_img_list = []
        for img in img_list:
            if 'http' not in img:
                img = 'http://www.gzjd.gov.cn' + img
            final_img_list.append(img)
        item['imageUrls'] = final_img_list
        if text.strip() == "" and len(img_list) == 0:
            return

        yield item
