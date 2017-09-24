#coding=utf-8
import scrapy

from ..items import YangshengwangItem
from ..spiders.beautifulSoup import processText
from datetime import datetime
from basespider import BaseTimeCheckSpider

class newsSpider(BaseTimeCheckSpider):
    name = "39health2new"
    dict_commens = {'ys/jkdsy': '2健康大视野',
        'ys/shyp': '2生活用品','ys/shcs': '2生活常识','ys/shxg': '2生活习惯','ys/yswq': '2养生误区',
        'ys/jj': '2居家保健','dzbj': '1保健人群','dzbj/woman': '2女性保健','dzbj/man': '2男性保健',
        'dzbj/oldman': '2老人保健','dzbj/baby': '2儿童保健','ys/mxys': '2名人养生',
        'jbyf/jzb': '2颈椎病','jbyf/az': '2癌症','jbyf/xxg': '2心血管','yjk/zzyf/sm': '2失眠',
        'yjk/zzyf/pl': '2疲劳','yjk/zzyf/zhz': '2综合症','ys/jkjj': '2健康纠结','ys/jkjj': '2养生指南'
    }
    start_urls = ['http://care.39.net/%s/' % x for x in dict_commens.keys()]

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

        item["module"] = "保健常识"
        item["className"] = response.xpath('//*[@class="ClassNav"]')[-2].xpath('text()').extract_first()
        item["specificName"] = response.xpath('//*[@class="ClassNav"]')[-1].xpath('text()').extract_first()
        item["classNum"] = 2
        item["title"] = response.xpath('//*[@id="art_box"]/div[1]/div[1]/h1/text()').extract_first()
        item["source"] = "39健康网"
        item["sourceUrl"] = response.url
        if response.xpath('//*[@id="contentText"]/p/img/@src').extract() is None:
            item["imageUrls"] = ''
        else:
            item["imageUrls"] = response.xpath('//*[@id="contentText"]/p/img/@src').extract()
        item["time"] = response.xpath('//*[@id="art_box"]/div[1]/div[1]/div[1]/div[2]/em[1]/text()').extract_first()

        text_list = response.xpath('//*[@id="contentText"]/*')
        if len(text_list) == 0:
            text_list = response.xpath('//*[@class="article"]/*')

        item["text"] = processText(text_list)

        yield item
