#coding=utf-8
import scrapy

from ..items import YangshengwangItem
from ..spiders.beautifulSoup import processText,processImg
from datetime import datetime
from basespider import BaseTimeCheckSpider

class newsSpider(BaseTimeCheckSpider):
    name = "39health3new"
    dict_commens = {'cjbj/yfjb', 'cjbj/ysmf', 'cjbj/stwl', 'cjbj/qjbj', 'xjbj/xrys',
        'xjbj/jblx', 'xjbj/fsmf', 'xjbj/jkts', 'qjbj/qjys', 'qjbj/qgqz', 'qjbj/qfqb',
        'qjbj/qjhf', 'djbj/fblx', 'djbj/ysyd', 'djbj/sthl', 'djbj/dljb'
    }

    start_urls = ['http://care.39.net/sjbj/%s/' % x for x in dict_commens]

    def parse(self, response):
        should_deep = True
        times = response.xpath('//*[@class="time"]/text()').extract()
        urls = response.xpath('//*[@class="listbox"]/ul/li/span/a/@href').extract()

        valid_child_urls = list()

        for time, url in zip(times, urls):
            try:
                final_time = time.split(' ')[0].split('/')[0]
                for part in time.split(' ')[0].split('/')[1:3]:
                    if len(part) > 1:
                        final_time =  final_time + '/' + part
                    else:
                        final_time = final_time + '/' + '0' + part
                final_time = final_time + ' ' + time.split(' ')[1]
                time_now = datetime.strptime(final_time, '%Y/%m/%d %H:%M:%S')
                self.update_last_time(time_now)
            except:
                print("Something Wrong")
                break

            if self.last_time is not None and self.last_time >= time_now:
                should_deep = False
                break

            valid_child_urls.append(url)

        next_requests = list()
        if should_deep:
            # 表示有新的url
            # 翻页
            if 'html' in response.url:
                num = int(response.url.split('_')[1][0])
                next_url = response.url.split('_')[0] + '_' + str(num + 1) + ".html"
            else:
                next_url = response.url + 'index_1.html'
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

        item["module"] = "健康资讯"
        item["className"] = '四季保健'
        item["specificName"] = response.xpath('//*[@class="ClassNav"]')[-2].xpath('text()').extract_first()
        item["classNum"] = 2
        item["title"] = response.xpath('//*[@id="art_box"]/div[1]/div[1]/h1/text()').extract_first()
        item["source"] = "39健康网"
        item["sourceUrl"] = response.url
        img_list = response.xpath('//*[@id="contentText"]').extract_first()
        item['imageUrls'] = processImg(img_list)
        item["time"] = response.xpath('//*[@id="art_box"]/div[1]/div[1]/div[1]/div[2]/em[1]/text()').extract_first()

        text_list = response.xpath('//*[@id="contentText"]/*')
        if len(text_list) == 0:
            text_list = response.xpath('//*[@class="article"]/*')

        item["text"] = processText(text_list)

        yield item
