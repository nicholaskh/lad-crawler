#coding=utf-8
import scrapy
import re

from ..items import YangshengwangItem
from ..spiders.beautifulSoup import processText, processImg
from datetime import datetime
from basespider import BaseTimeCheckSpider

class newsSpider(BaseTimeCheckSpider):
    name = "yanhuang1"
    dict_commens = {
        'yinshi/shiliao': '食疗养生&饮食养生',
        'yinshi/shipu': '养生食谱&饮食养生',
        'yinshi/yingyang': '营养饮食&饮食养生',
        'yinshi/jinji': '食物禁忌&饮食养生',
        'renqun/nanxing': '男性保健&保健人群',
        'renqun/nvxing': '女性保健&保健人群',
        'renqun/laoren': '老人保健&保健人群',
        'renqun/ertong': '儿童保健&保健人群',
        'renqun/bailing': '白领养生&保健人群',
        'renqun/mingren': '名人养生&保健人群',
        'jijie/chunji':'春季保健&四季保健',
        'jijie/xiaji':'夏季保健&四季保健',
        'jijie/qiuji':'秋季保健&四季保健',
        'jijie/dongji':'冬季保健&四季保健'
        }
    start_urls = ['http://www.yhys.com/%s/' % x for x in dict_commens.keys()]

    def parse(self, response):
        should_deep = True
        times = response.xpath('//*[@class="news_span1"]/text()').extract()
        urls = response.xpath('//*[@class="news"]/a/@href').extract()

        valid_child_urls = list()

        for time, url in zip(times, urls):
            try:
                final_time = time
                time_now = datetime.strptime(final_time, '%Y-%m-%d')
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
                num = int(response.url.split('_')[1].split('.')[0])
                next_url = response.url.split('_')[0] + '_' + str(num + 1) + ".html"
            else:
                next_url = response.url + 'index_2.html'
            next_requests.append(scrapy.Request(url=next_url, callback=self.parse))

        for index, temp_url in enumerate(valid_child_urls):
            req = scrapy.Request(url=temp_url, callback=self.parse_info)

            hit_time = times[index]
            m_item = YangshengwangItem()
            m_item['time'] = hit_time
            m_item["classNum"] = 2
            if 'html' in response.url:
                key_word = re.search('com/(.+)/index', response.url).group(1)
            else:
                key_word = re.search('com/(.+)/', response.url).group(1)
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
        item["title"] = response.xpath('//*[@class="con_left_title"]/h1/text()').extract_first()
        item["source"] = "炎黄养生网"
        item["sourceUrl"] = response.url
        img_list = response.xpath('//*[@class="content_text"]').extract_first()
        item['imageUrls'] = processImg(img_list)
        item["time"] = response.xpath('//*[@class="info"]/span[2]/text()').extract_first()[3:13]

        text_list = response.xpath('//*[@class="content_text"]/*')
        item["text"] = processText(text_list)

        yield item
