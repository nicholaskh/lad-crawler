#coding=utf-8
import scrapy

from ..items import YangshengwangItem
from ..spiders.beautifulSoup import processText,processImg
from datetime import datetime
from basespider import BaseTimeCheckSpider

class newsSpider(BaseTimeCheckSpider):
    name = "39health7new"
    dict_news = {'interview': '1医药名人堂'}
    start_urls = ['http://news.39.net/%s/' % x for x in dict_news.keys()]

    def parse(self, response):

        should_deep = True

        times = response.xpath('//*[@class="time"]/text()').extract()
        urls = response.xpath('//*[@class="listbox"]/ul/li/span/a/@href').extract()

        valid_child_urls = list()

        for time, url in zip(times, urls):
            try:
                time_now = datetime.strptime(time.encode('utf-8'), '%Y/%m/%d %H:%M:%S')
                self.update_last_time(time_now)
            except:
                break

            if self.last_time is not None and self.last_time >= time_now:
                should_deep = False
                break

            valid_child_urls.append(url)

        next_requests = list()
        if should_deep:
            # 表示有新的url
            # 翻页
            if len(response.url) <= 29:
                next_url = response.url + 'index_1.html'
            else:
                num = int(response.url.split('_')[1][0])
                next_url = response.url.split('_')[0] + '_' + str(num + 1) + ".html"
            next_requests.append(scrapy.Request(url=next_url, callback=self.parse))

        for index, temp_url in enumerate(valid_child_urls):
            req = scrapy.Request(url=temp_url, callback=self.parse_info)

            hit_time = times[index]
            m_item = YangshengwangItem()
            m_item['time'] = hit_time
            req.meta['item'] = m_item
            next_requests.append(req)

        for req in next_requests:
            yield req

    def parse_info(self, response):
        item = response.meta['item']

        item["module"] = "健康资讯"
        key_name = response.url.split('/')[3]
        len_str = len(self.dict_news[key_name])
        item["className"] = self.dict_news[key_name][1:len_str]
        item["classNum"] = 1
        item["title"] = response.xpath('//*[@id="art_box"]/div[1]/div[1]/h1/text()').extract_first()
        item["source"] = "39健康网"
        item["sourceUrl"] = response.url
        item['imageUrls'] = processImg(response.xpath('//*[@id="contentText"]').extract_first())
        item["time"] = response.xpath('//*[@id="art_box"]/div[1]/div[1]/div[1]/div[2]/em[1]/text()').extract_first()

        text_list = response.xpath('//*[@id="contentText"]/*')
        if len(text_list) == 0:
            text_list = response.xpath('//*[@class="article"]/*')

        item["text"] = processText(text_list)

        yield item
