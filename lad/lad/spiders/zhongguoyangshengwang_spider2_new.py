#coding=utf-8
import scrapy
import re

from ..items import YangshengwangItem
from ..spiders.beautifulSoup import processText, processImgSep2
from datetime import datetime
from basespider import BaseTimeCheckSpider

class newsSpider(BaseTimeCheckSpider):
    name = "zhongguo2"
    text = ''
    dict_commens = {
        'shuhuaxiaochangshi':'书画小常识'
        # 'jianshangchangshi':'鉴赏常识',
        # 'shuhuayuyangsheng':'书画与养生',
        # 'huodongdongtai':'活动动态',
        # 'shuhuamingrenzhishi':'书画名人轶事',
        # 'dashizuopin':'作品欣赏'
        }
    start_urls = ['http://www.cpoha.com.cn/shuhua/%s/' % x for x in dict_commens.keys()]

    def parse(self, response):
        should_deep = True
        times = response.xpath('//*[@class="listbox"]/ul/li/span/text()[2]').extract()
        urls = response.xpath('//*[@class="listbox"]/ul/li/a/@href').extract()

        valid_child_urls = list()

        for time, url in zip(times, urls):
            try:
                final_time = time.strip()[:19]
                time_now = datetime.strptime(final_time, '%Y-%m-%d %H:%M:%S')
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
                    print("**********************")
                    next_part_url = response.xpath('//*[@class="pagelist"]/li')[-3].xpath('a/@href').extract_first()
                    if 'html' not in response.url:
                        next_url = response.url + next_part_url
                    else:
                        next_url = 'http://www.cpoha.com.cn/' + response.url.split('/')[3] + '/' + response.url.split('/')[4] + '/' + next_part_url
                    print('next_url')
                    print(next_url)
            else:
                next_url = None
            yield scrapy.Request(url=next_url, callback=self.parse)

        for index, temp_url in enumerate(valid_child_urls):
            req = scrapy.Request(url=temp_url, callback=self.parse_info)

            hit_time = times[index]
            m_item = YangshengwangItem()
            m_item["classNum"] = 1
            key_word = re.search('shuhua/(.+)/', response.url).group(1)
            total_str = self.dict_commens[key_word]
            m_item["className"] = total_str
            m_item["next_father_url"] = response.url
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
        item["time"] = response.xpath('//*[@id="pub_date"]/text()').extract_first()
        item["sourceUrl"] = response.url

        text_list = response.xpath('//*[@id="content"]/p/text()')
        for p_slt in text_list:
            self.text = self.text + p_slt.extract()
        item["text"] = self.text.strip()
        if len(item["text"]) < 25:
            text_list = response.xpath('//*[@id="content"]/*')
            item["text"] = processText(text_list)
        self.text = ""
        img_list = response.xpath('//*[@id="content"]/*')
        imageUrls_list = processImgSep2(img_list)

        yield item
