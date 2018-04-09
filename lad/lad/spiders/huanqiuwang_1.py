#coding=utf-8
import scrapy

from ..items import DailyNewsItem
from ..spiders.beautifulSoup import processText, processImgSep
from datetime import datetime
from .basespider import BaseTimeCheckSpider

class newsSpider(BaseTimeCheckSpider):
    name = "huanqiuwang_1"
    dict_commens = {
        'http://world.huanqiu.com/exclusive/': '国际',
        'http://lianghui.huanqiu.com/2018/roll/': '政治',
        'http://society.huanqiu.com/article/': '社会',
        'http://society.huanqiu.com/societylaw/': '社会',
        'http://society.huanqiu.com/socialnews/': '社会',
        'http://society.huanqiu.com/anecdotes/': '社会',
        'http://finance.huanqiu.com/gjcx/': '经济',
        'http://world.huanqiu.com/regions/': '国际',
        'http://oversea.huanqiu.com/article/': '国际',
        'http://ski.huanqiu.com/news/': '体育',
        'http://china.huanqiu.com/leaders/': '政治',
        'http://china.huanqiu.com/fanfu/': '政治',
        'http://mil.huanqiu.com/world/': '军事',
        'http://mil.huanqiu.com/strategysituation/': '军事',
    }
    start_urls = ['%s' % x for x in dict_commens.keys()]

    def parse(self, response):
        times = response.xpath('//div[@class="fallsFlow"]/ul/li/h6/text()').extract()
        urls = response.xpath('//div[@class="fallsFlow"]/ul/li/h3/a/@href').extract()
        valid_child_urls = list()

        for time, url in zip(times, urls):
            try:
                time_now = datetime.strptime(time.split(' ')[0], '%Y-%m-%d')
                self.update_last_time(time_now)
            except:
                print("Something Wrong")
                break

            if self.last_time is not None and self.last_time >= time_now:
                break
            valid_child_urls.append(url)

        for index, temp_url in enumerate(valid_child_urls):
            req = scrapy.Request(url=temp_url, callback=self.parse_info)
            hit_time = times[index]
            m_item = DailyNewsItem()
            m_item['time'] = hit_time.split(' ')[0]
            key_word = response.url
            class_name = self.dict_commens[key_word]
            m_item['className'] = class_name
            # 相当于在request中加入了item这个元素
            req.meta['item'] = m_item
            yield req

    def parse_info(self, response):
        item = response.meta['item']
        item["source"] = "环球网"
        title = response.xpath('//h1[@class="tle"]/text()').extract_first()
        if title is None:
            return
        item["title"] = title
        item["sourceUrl"] = response.url
        text_list = response.xpath('//div[@class="la_con"]/p')
        text = processText(text_list)
        item["text"] = text
        img_list = processImgSep(text_list)
        final_img_list = []
        for img in img_list:
            if 'http' in img:
                final_img_list.append(img)
        item['imageUrls'] = final_img_list
        if text.strip().replace("$#$", "") == "":
            return

        yield item
