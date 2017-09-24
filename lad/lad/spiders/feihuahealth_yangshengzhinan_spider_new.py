#coding=utf-8
import scrapy

from ..items import YangshengwangItem
from ..spiders.beautifulSoup import processText
from datetime import datetime
from basespider import BaseTimeCheckSpider

class newsSpider(BaseTimeCheckSpider):
    name = "feihua1new"
    start_urls = ['http://care.fh21.com.cn/yszn/']

    def parse(self, response):

        should_deep = True

        times = response.xpath('//*[@class="ma-modone-right-time"]/text()').extract()
        urls = response.xpath('//*[@class="ma-modone-right fl"]/a/@href').extract()

        valid_child_urls = list()

        for time, url in zip(times, urls):
            try:
                time_now = datetime.strptime(time.strip(), '%Y-%m-%d %H:%M')
                self.update_last_time(time_now)
            except:
                break

            if self.last_time is not None and self.last_time >= time_now:
                should_deep = False
                break

            valid_child_urls.append('http://care.fh21.com.cn' + url)

        next_requests = list()
        if should_deep:
            # 表示有新的url
            # 翻页
            if response.xpath('//*[@class="wrap-list-paging mt-20"]/p/a/text()').extract()[-2].encode('utf-8') == '下一页':
                #判断是否是最后一页,不是的话执行下面逻辑
                if len(response.url) == 29:
                    next_url = 'http://care.fh21.com.cn/yszn/list_6529_2.html'
                else:
                    num = int(response.url.split('_')[2][0])
                    next_url = 'http://care.fh21.com.cn/yszn/list_6529_' + str(num + 1) + ".html"
                next_requests.append(scrapy.Request(url=next_url, callback=self.parse))

        for index, temp_url in enumerate(valid_child_urls):
            req = scrapy.Request(url=temp_url, callback=self.parse_info)

            hit_time = times[index]
            m_item = YangshengwangItem()
            m_item['time'] = hit_time
            # 相当于在request中加入了item这个元素
            req.meta['item'] = m_item
            next_requests.append(req)

        for req in next_requests:
            yield req

    def parse_info(self, response):
        item = response.meta['item']

        item["module"] = "保健常识"
        item["className"] = "养生指南"
        item["classNum"] = 1
        item["title"] = response.xpath('//*[@class="arti-head"]/h2/text()').extract_first()
        item["source"] = "飞华保健网"
        item["sourceUrl"] = response.url
        if response.xpath('//*[@style="text-align: center;"]/img/@src').extract() is None:
            item["imageUrls"] = ''
        else:
            item["imageUrls"] = response.xpath('//*[@style="text-align: center;"]/img/@src').extract()
        item["time"] = response.xpath('/html/body/div[4]/div/div[1]/div[2]/div[1]/div/span/text()').extract_first().strip().split(' ')[1]

        text_list = response.xpath('//*[@class="arti-content"]/*')

        item["text"] = processText(text_list)

        yield item
