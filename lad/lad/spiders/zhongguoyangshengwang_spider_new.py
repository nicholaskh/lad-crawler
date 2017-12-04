#coding=utf-8
import scrapy
import re

from ..items import YangshengwangItem
from ..spiders.beautifulSoup import processText, processImgSep2
from datetime import datetime
from basespider import BaseTimeCheckSpider

class newsSpider(BaseTimeCheckSpider):
    name = "zhongguo1"
    text = ''
    dict_commens = {
        'yangsheng/yangshengwenxian':'养生文献&养生文化'
        }
    start_urls = ['http://www.cpoha.com.cn/%s/' % x for x in dict_commens.keys()]

    def parse(self, response):
        should_deep = True
        times = response.xpath('//*[@class="listbox"]/ul/li/span/text()[2]').extract()
        urls = response.xpath('//*[@class="listbox"]/ul/li/a/@href').extract()

        valid_child_urls = list()

        for time, url in zip(times, urls):
            try:
                final_time = time.strip()[:10]
                time_now = datetime.strptime(final_time, '%Y-%m-%d')
                self.update_last_time(time_now)
            except:
                print("Something Wrong")
                break

            if self.last_time is not None and self.last_time >= time_now:
                should_deep = False
                break

            valid_child_urls.append('http://www.cpoha.com.cn' + url)

        next_requests = list()
        if should_deep:
            # 表示有新的url
            # 翻页
            if len(response.xpath('//*[@class="pagelist"]/li')[-3].xpath('a/text()')) > 0 :
                if response.xpath('//*[@class="pagelist"]/li')[-3].xpath('a/text()').extract_first().encode('utf-8') == '下一页':
                    next_part_url = response.xpath('//*[@class="pagelist"]/li')[-3].xpath('a/@href').extract_first()
                    if 'html' not in response.url:
                        next_url = response.url + next_part_url
                    else:
                        next_url = 'http://www.cpoha.com.cn/' + response.url.split('/')[3] + '/' + response.url.split('/')[4] + '/' + next_part_url
                    yield scrapy.Request(url=next_url, callback=self.parse)

        for index, temp_url in enumerate(valid_child_urls):
            req = scrapy.Request(url=temp_url, callback=self.parse_info)

            hit_time = times[index]
            m_item = YangshengwangItem()
            m_item['time'] = hit_time[:10]
            m_item["classNum"] = 2
            if 'html' in response.url:
                key_word = response.url.split('/')[3] + '/' + response.url.split('/')[4]
                print('########')
                print(key_word)
            else:
                key_word = re.search('http://www.cpoha.com.cn/(.+)/', response.url).group(1)
                print('########')
                print(key_word)
            total_str = self.dict_commens[key_word]
            m_item["className"] = total_str.split('&')[1]
            m_item["specificName"] = total_str.split('&')[0]
            # 相当于在request中加入了item这个元素
            req.meta['item'] = m_item
            next_requests.append(req)

        for req in next_requests:
            yield req

    def parse_info(self, response):
        item = response.meta['item']

        item["module"] = "健康资讯"
        item["title"] = response.xpath('//*[@class="left w640"]/h1/text()').extract_first()
        item["source"] = "中国养生网"
        item["sourceUrl"] = response.url

        text_list = response.xpath('//*[@id="content"]/p/text()')
        for p_slt in text_list:
            self.text = self.text + p_slt.extract()
        item["text"] = self.text
        if len(item["text"]) < 20:
            text_list = response.xpath('//*[@id="content"]/*')
            item["text"] = processText(text_list)
        self.text = ""
        img_list = response.xpath('//*[@id="content"]/*')
        imageUrls_list = processImgSep2(img_list)

        yield item
