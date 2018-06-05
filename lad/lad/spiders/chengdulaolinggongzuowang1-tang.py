#coding=utf-8
import scrapy
import re

from ..items import YanglaoItem
from ..spiders.beautifulSoup import processText, processImgSep
from datetime import datetime
from .basespider import BaseTimeCheckSpider

class newsSpider(BaseTimeCheckSpider):
    name = 'chengdulaolinggongzuowang1'
    start_urls = ['http://www.cdllb.org.cn/llwgzw/zcfg/list.shtml']

    def parse(self, response):
        should_deep = True
        times= response.xpath('//*[@id="xlist"]//li/span/text()').extract()
        if len(times) == 0:
            should_deep =False

        #是相对链接
        urls_ori = response.xpath('//*[@id="xlist"]//li/a/@href').extract()
        urls = []
        for each in urls_ori:
            if 'http://' not in each:
                url = 'http://www.cdllb.org.cn' + each
                urls.append(url)
        #titles_ori = response.xpath('//td[@valign="top"]/table[1]').extract()
        #titles = re.findall('title="(.*?)">', str(titles_ori))
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
            #url = 'http://www.ahllb.cn' + url
            valid_child_urls.append(url)

        next_requests = list()
        # if should_deep:
        #     #maxPageNum = int(response.xpath('//div[@class="pagenum_label"]//dd/p/text()').extract()[0].strip())
        #     currentPageNum = int(response.url.split('=')[-1])
        #
        #     nextPageNum = currentPageNum + 1
        #     if nextPageNum > 5:
        #         return
        #
        #     next_url = 'http://www.hkllb.cn/list.asp?id=1&PageNo=' + str(nextPageNum)
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

        item["source"] = "成都老龄工作网"

        # title_ori =  response.xpath('//div[@class="w96"]/h1/text() | //div[@class="w96"]/h1/span/text()').extract()
        # title =''
        # for each in title_ori:
        #     title = title + each
        title = response.xpath('//h1[@class="titleC1"]/text()').extract()[0]
        if len(title) == 0:
            return
        item["title"] = title


        item["sourceUrl"] = response.url
        # 修改了text_list
        #text_list = response.xpath('//*[@id="ivs_content"]/p/text() | //*[@id="ivs_content"]/p//font/text()')
        text_list = response.xpath('//div[@id="myTable"]//p')
        text = processText(text_list)
        item["text"] = text
        if len(text) <= 10:
            return

        text_list = response.xpath('//div[@id="myTable"]//p')
        img_list = processImgSep(text_list)
        final_img_list = []
        img_url = 'www.cdllb.org.cn'
        for i in range(3, len(response.url.split('/')) - 1):
            img_url = img_url + '/' + response.url.split('/')[i]
        for img in img_list:
            if 'http' not in img:
                img = img_url + '/' + img
                img = 'http://' + img
            final_img_list.append(img)
        item['imageUrls'] = final_img_list
        if text.strip() == "" and len(img_list) == 0:
            return

        yield item
