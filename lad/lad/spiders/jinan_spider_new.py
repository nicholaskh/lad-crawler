#coding=utf-8
import scrapy

from ..items import LadItem
from ..spiders.beautifulSoup import processText
from datetime import datetime
from basespider import BaseTimeCheckSpider

class newsSpider(BaseTimeCheckSpider):
    name = "jinannew"
    start_urls = ['http://www.jnmsjw.gov.cn/channels/209.html']
    text = ""

    def parse(self, response):

        should_deep = True

        times = response.xpath('//*[@class="children"]/li/span/text()').extract()
        urls = response.xpath('//*[@id="left"]/div/ul/li/a/@href').extract()

        valid_child_urls = list()

        for time, url in zip(times, urls):
            try:
                time_now = datetime.strptime(time, '%Y-%m-%d')
                self.update_last_time(time_now)
            except:
                break

            if self.last_time is not None and self.last_time >= time_now:
                should_deep = False
                break
            append_url = "http://www.jnmsjw.gov.cn" + url
            print("7777777")
            print(append_url)
            valid_child_urls.append(append_url)

        next_requests = list()
        if should_deep:
            # 表示有新的url
            # 翻页
            if len(response.xpath('//*[@id="left"]/div/ul/li/a/@href')) == 15:
                #判断是否是最后一页,不是的话执行下面逻辑
                if len(response.url) == 42:
                    next_url = 'http://www.jnmsjw.gov.cn/channels/209_2.html'
                else:
                    num = int(response.url.split('_')[1][0])
                    next_url = 'http://www.jnmsjw.gov.cn/channels/209_' + str(num + 1) + ".html"
            next_requests.append(scrapy.Request(url=next_url, callback=self.parse))

        for index, temp_url in enumerate(valid_child_urls):
            req = scrapy.Request(url=temp_url, callback=self.parse_info)

            hit_time = times[index]
            m_item = LadItem()
            m_item['time'] = hit_time
            # 相当于在request中加入了item这个元素
            req.meta['item'] = m_item
            next_requests.append(req)

        for req in next_requests:
            yield req

    def parse_info(self, response):
        item = response.meta['item']

        item["city"] = "济南公安网"
        item["sourceUrl"]
        item["newsType"] = "警事要闻"
        item["title"] = response.xpath('//*[@id="content-title"]/h3/text()').extract_first()
        item["time"] = response.xpath('//*[@id="content-title"]/text()').extract()[1].strip()[0:10]

        text_list = response.xpath('//*[@id="content"]/p/span/text()')
        if len(text_list) == 0:
            text_list = response.xpath('//*[@id="content"]/div/div/p/span/text()')
        if len(text_list) == 0:
            text_list = response.xpath('//*[@id="content"]/div/div/div/p/span/text()')

        for p_slt in text_list:
            if p_slt.extract() is None:
                self.text = self.text
            else:
                self.text = self.text + p_slt.extract()
        item["text"] = self.text
        self.text = ""

        yield item
