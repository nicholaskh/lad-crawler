#coding=utf-8
import scrapy
import re

from ..items import YanglaoItem
from ..spiders.beautifulSoup import processText, processImgSep
from datetime import datetime
from .basespider import BaseTimeCheckSpider

class newsSpider(BaseTimeCheckSpider):
    name = "guangdonglaolingwang1"
    start_urls = ['http://www.gdllw.org/zcfg/default.htm']

    def parse(self, response):
        should_deep = True

        times_ori =  response.xpath('//div[@class="article_list_news"]/ul//li/span/text()').extract()
        if len(times_ori) == 0:
            should_deep =False
        times = []
        for each in times_ori:
            times.append(each[1:-1])

        #是相对链接
        urls_ori = response.xpath('//div[@class="article_list_news"]/ul//li/a/@href').extract()
        urls = []
        for each in urls_ori:
            each = 'http://www.gdllw.org/zcfg' + each[1:]
            urls.append(each)

        titles = response.xpath('//div[@class="article_list_news"]/ul//li/a/text()').extract()

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
        if should_deep:
            #maxPageNum = int(response.xpath('//div[@class="pagenum_label"]//dd/p/text()').extract()[0].strip())
            if '_' in response.url:
                currentPageNum =int(response.url.split('_')[-1].split('.')[0])
            else:
                currentPageNum = 0

            nextPageNum = currentPageNum + 1
            if nextPageNum > 10:
                return

            next_url = 'http://www.gdllw.org/zcfg/default_' + str(nextPageNum) + '.htm'
            req = scrapy.Request(url=next_url, callback=self.parse)
            yield req

        for index, temp_url in enumerate(valid_child_urls):
            req = scrapy.Request(url=temp_url, callback=self.parse_info)
            m_item = YanglaoItem()
            #m_item['title'] = titles[index]
            m_item['time'] = times[index]
            m_item['title'] = titles[index]
            m_item['className'] = '政策法规'
            req.meta['item'] = m_item
            yield req

    def parse_info(self, response):
        item = response.meta['item']

        item["source"] = "广东老龄网"

        # title_ori =  response.xpath('//div[@class="w96"]/h1/text() | //div[@class="w96"]/h1/span/text()').extract()
        # title =''
        # for each in title_ori:
        #     title = title + each
        #item["title"] = response.xpath('/html/body/div[3]/div[1]/h3/text()').extract()[0]

        item["sourceUrl"] = response.url
        # 修改了text_list
        #text_list = response.xpath('//*[@id="ivs_content"]/p/text() | //*[@id="ivs_content"]/p//font/text()')
        text_list = response.xpath('//div[@class="TRS_Editor"]/*')
        text = processText(text_list)
        item["text"] = text

        text_list = response.xpath('//div[@class="TRS_Editor"]/*')
        img_list = processImgSep(text_list)
        final_img_list = []
        for img in img_list:
            if 'http' not in img:
                img_ori = response.url.split('/')
                image = 'http://'
                for i in range(2, len(img_ori) - 1):
                    image = image + img_ori[i] + '/'
                image = image + img[2:]
            final_img_list.append(image)

        item['imageUrls'] = final_img_list
        if text.strip() == "" and len(img_list) == 0:
            return

        yield item
