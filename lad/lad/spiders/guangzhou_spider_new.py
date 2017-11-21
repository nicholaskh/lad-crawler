#coding=utf-8
import scrapy

from ..items import LadItem
from ..spiders.beautifulSoup import processText,processImgSep1
from datetime import datetime
from basespider import BaseTimeCheckSpider

class newsSpider(BaseTimeCheckSpider):
    name = "guangzhounew"
    start_urls = ['http://www.gzjd.gov.cn/gzjdw/gaxw/ztbd/ffzp/index.shtml']

    def parse(self, response):

        should_deep = True

        times = response.xpath('//*[@class="read_more"]/td/span/text()').extract()
        urls = response.xpath('/html/body/div[2]/section/div/div[2]/div[2]/ul/li/table/tr[1]/td/dl/dt/a/@href').extract()

        valid_child_urls = list()

        for time, url in zip(times, urls):
            try:
                time_now = datetime.strptime(time[:10], '%Y-%m-%d')
                self.update_last_time(time_now)
            except:
                break

            if self.last_time is not None and self.last_time >= time_now:
                should_deep = False
                break

            valid_child_urls.append('http://www.gzjd.gov.cn' + url)

        next_requests = list()
        if should_deep:
            if response.xpath('/html/body/div[2]/section/div/div[2]/div[2]/ul/li/table/tr/td/span/text()')[9].extract()[0:9] != '2001-7-12':
                #判断是否是最后一页,不是的话执行下面逻辑
                if len(response.url) == 55:
                    next_url = "http://www.gzjd.gov.cn/gzjdw/gaxw/ztbd/ffzp/list-2.shtml"
                else:
                    part_str = response.url.split('/')[7]
                    num = int(part_str[5])
                    next_url_part = "list-" + str(num + 1) + ".shtml"
                    next_url = "http://www.gzjd.gov.cn/gzjdw/gaxw/ztbd/ffzp/" + next_url_part
            next_requests.append(scrapy.Request(url=next_url, callback=self.parse))

        for index, temp_url in enumerate(valid_child_urls):
            req = scrapy.Request(url=temp_url, callback=self.parse_info)

            hit_time = times[index][:10]
            m_item = LadItem()
            m_item['time'] = hit_time
            # 相当于在request中加入了item这个元素
            req.meta['item'] = m_item
            next_requests.append(req)

        for req in next_requests:
            yield req

    def parse_info(self, response):
        item = response.meta['item']

        item["city"] = "广州公安网"
        item["newsType"] = "警事要闻"
        item["sourceUrl"] = response.url
        item["title"] = response.xpath('//*[@class="news_content_header"]/dl/dt/text()').extract_first().strip()
        # item["time"] = response.xpath('/html/body/table[4]/tr/td/table[4]/tr/td/text()[1]').extract_first().strip()[10:21]
        text_list = response.xpath('//*[@class="news_content_txt2"]/*')
        item["text"] = processText(text_list)
        item["imageUrls"] = processImgSep1(response.xpath('//*[@class="news_content_txt2"]').extract_first())

        yield item
