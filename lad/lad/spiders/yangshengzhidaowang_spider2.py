# coding=utf-8

import scrapy

from ..items import YangshengItem
from ..spiders.beautifulSoup import processText
from datetime import datetime
from basespider import BaseTimeCheckSpider


class NewsSpider(BaseTimeCheckSpider):

    name = "yangshengzhidaowang2"
    start_urls = ['https://www.ys137.com/xinwen']
    news_type = ""
    text = ""

    def parse(self, response):

        should_deep = True

        times = response.xpath('//*[@class="arc-tags clearfix"]/*[@class="pull-right"]/text()').extract()
        urls = response.xpath('//*[@class="arc-infos clearfix"]/a/@href').extract()

        valid_child_urls = list()

        for time, url in zip(times, urls):
            # 打包times, urls 返回一个元组
            try:
                time_now = datetime.strptime(time, '%Y-%m-%d %H:%M')

                # 更新将要保存到MONGODB中的时间
                self.update_last_time(time_now)
            except:
                break

            if self.last_time is not None and self.last_time >= time_now:
                should_deep = False
                # 时间越近越大
                # 爬过了
                break
            # 要爬的url
            valid_child_urls.append(url)

        next_requests = list()
        if should_deep:
            # 表示有新的url
            next_url = response.xpath('/html/body/div/div/div/ul/li/a/@href').extract()[-1]
            if next_url != '#':
                next_url = 'https://www.ys137.com/xinwen/%s' % next_url
                next_requests.append(scrapy.Request(url=next_url, callback=self.parse))

        for index, temp_url in enumerate(valid_child_urls):
            req = scrapy.Request(url=temp_url, callback=self.parse_info)

            hit_time = times[index]
            m_item = YangshengItem()
            m_item['time'] = hit_time

            req.meta['item'] = m_item
            next_requests.append(req)

        for req in next_requests:
            yield req

    @staticmethod
    def parse_info(response):
        item = response.meta['item']

        item["web"] = "养生之道网"
        item["title"] = response.xpath('/html/body/div/div/h1/text()').extract_first()
        item["yangshengType"] = "养生资讯"
        text_list = response.xpath('/html/body/div/div/div/table/tr/td/*')
        item["text"] = processText(text_list)

        yield item
