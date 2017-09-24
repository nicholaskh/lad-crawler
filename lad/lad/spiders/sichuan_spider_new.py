#coding=utf-8
import scrapy

from ..items import LadItem
from ..spiders.beautifulSoup import processText
from datetime import datetime
from basespider import BaseTimeCheckSpider

class NewsSpider(BaseTimeCheckSpider):

    name = "sichuannew"
    start_urls = ['http://www.scga.gov.cn/jwzx/gdjx/index.html']
    text = ""

    def parse(self, response):

        next_url = None
        if '24' not in response.url:
            #判断是否是最后一页,不是的话执行下面逻辑
            if len(response.url) == 43:
                next_url = "http://www.scga.gov.cn/jwzx/gdjx/index_1.html"
            else:
                part_str = response.url.split('/')[5]
                num = int(part_str[6])
                next_url_part = "index_" + str(num + 1) + ".html"
                next_url = "http://www.scga.gov.cn/jwzx/gdjx/" + next_url_part

        child_urls = response.xpath('/html/body/div[4]/div[1]/ul/li/a/@href')
        for infoDiv in child_urls[:-1]:
            part_url = infoDiv.extract()
            url_leng = len(part_url)
            part_url_sec = part_url[1:url_leng]
            n_url = 'http://www.scga.gov.cn/jwzx/gdjx' + part_url_sec
            child_request = scrapy.Request(url=n_url, callback=self.parse_info)
            m_item = LadItem()
            m_item['is_final_child'] = False
            child_request.meta['item'] = m_item
            yield child_request

        # 特殊处理最后一个，通过request的meta传递信息
        print('最后一个')
        final_child_url = child_urls[-1].extract()
        url_leng = len(final_child_url)
        part_url_sec = final_child_url[1:url_leng]
        n_url = 'http://www.scga.gov.cn/jwzx/gdjx' + part_url_sec
        print('######')
        print(n_url)
        final_request = scrapy.Request(url=n_url, callback=self.parse_info)
        m_item = LadItem()
        m_item['is_final_child'] = True
        m_item['next_father_url'] = next_url
        final_request.meta['item'] = m_item

        yield final_request

    def parse_info(self, response):
        item = response.meta['item']
        time = '20' + response.xpath('/html/body/div[4]/div[1]/div/table[1]/tr/td[2]/text()').extract_first().split('20')[1]

        try:
            time_now = datetime.strptime(time, '%Y-%m-%d %H:%M:%S')
            # 更新将要保存到MONGODB中的时间
            self.update_last_time(time_now)
        except:
            return

        if self.last_time is not None and self.last_time >= time_now:
            print(u'spider: %s 这篇文章已经存在' % self.url)
            return
        # next_requests = list()
        #if should_deep:
        # 表示有新的url
        item["sourceUrl"] = response.url
        item["city"] = "四川"
        item["newsType"] = "警事要闻"
        item["title"] = response.xpath('/html/body/div[4]/div[1]/div/div[1]/text()').extract_first()
        item["time"] = '20' + response.xpath('/html/body/div[4]/div[1]/div/table[1]/tr/td[2]/text()').extract_first().split('20')[1].split(' ')[0]

        text_list = response.xpath('//*[@id="Zoom"]/div[1]/div/div/p/font/font/font/font/font/span')
        if len(text_list) == 0:
            text_list = response.xpath('//*[@id="Zoom"]/div[1]/div/div/p/font/font/font/font/span')
        if len(text_list) == 0:
            text_list = response.xpath('//*[@id="Zoom"]/div[1]/div/div/p/font/font/font/span')
        if len(text_list) == 0:
            text_list = response.xpath('//*[@id="Zoom"]/div[1]/div/div/p/font/font/span')
        if len(text_list) == 0:
            text_list = response.xpath('//*[@id="Zoom"]/div[1]/div/div/p/span')
        if len(text_list) == 0:
            text_list = response.xpath('//*[@id="Zoom"]/div[1]/div/p/font')

        for str_slt in text_list:
            if str_slt.xpath('text()').extract_first() is None:
                self.text = self.text
            else:
                self.text = self.text + str_slt.xpath('text()').extract_first()
        item["text"] = self.text
        self.text = ""

        yield item

        # 在最后一个孩子哪儿判断是否需要爬取下一页，如果代码没有执行到这儿，那么说明下一页的时间已经是无效的时间了
        if item['is_final_child'] and item['next_father_url'] is not None:
            yield scrapy.Request(url=item['next_father_url'], callback=self.parse)
