#coding=utf-8
import scrapy
import re

from ..items import DailyNewsItem
from ..spiders.beautifulSoup import processText, processImgSep
from datetime import datetime
from .basespider import BaseTimeCheckSpider

class newsSpider(BaseTimeCheckSpider):
    name = "chinanews_1"
    dict_commens = {
        # 'http://channel.chinanews.com/cns/cl/ty-klsk.shtml?pager=0': '体育',
        # 'http://channel.chinanews.com/cns/cl/ty-bdjj.shtml?pager=0': '体育',
        # 'http://channel.chinanews.com/cns/cl/ty-gnzq.shtml?pager=0': '体育',
        # 'http://channel.chinanews.com/cns/cl/fz-jdrw.shtml?pager=0': '体育',
        'http://channel.chinanews.com/u/rdzz.shtml?pager=0': '体育',
        'http://channel.chinanews.com/cns/cl/gj-zxsjg.shtml?pager=0': '体育',
        'http://channel.chinanews.com/cns/cl/gn-gcdt.shtml?pager=0': '体育',
        'http://finance.chinanews.com/cj/gd.shtml?pager=0': '体育'
    }
    start_urls = ['%s' % x for x in dict_commens.keys()]

    def parse(self, response):
        should_deep = True
        times = response.xpath('//div[@class="con2"]/table/tr[1]/td[2]/text()').extract()
        # 判断末页
        if len(times) == 0:
            return
        #格式不规范
        urls = response.xpath('//div[@class="con2"]/table/tr[1]/td[1]/a/@href').extract()
        valid_child_urls = list()

        for time, url in zip(times, urls):
            try:
                time_now = datetime.strptime(time.split(' ')[0], '%Y-%m-%d')
                self.update_last_time(time_now)
            except:
                print("Something Wrong")
                break

            if self.last_time is not None and self.last_time >= time_now:
                should_deep = False
                break
            # 变成绝对url
            url = url.strip()
            valid_child_urls.append(url)

        next_requests = list()
        if should_deep:
            current_page = int(response.url.rsplit('=', 1)[-1])
            next_url = response.url.rsplit('=', 1)[0] + "=" + str(current_page + 1)
            next_requests.append(scrapy.Request(url=next_url, callback=self.parse))

        for index, temp_url in enumerate(valid_child_urls):
            req = scrapy.Request(url=temp_url, callback=self.parse_info)

            hit_time = times[index]
            m_item = DailyNewsItem()
            m_item['time'] = hit_time.split(' ')[0]
            key_word = response.url.rsplit('?', 1)[0] + "?pager=0"
            class_name = self.dict_commens[key_word]
            m_item['className'] = class_name
            # 相当于在request中加入了item这个元素
            req.meta['item'] = m_item
            next_requests.append(req)

        for req in next_requests:
            yield req

    def parse_info(self, response):
        item = response.meta['item']

        title = response.xpath('//*[@id="cont_1_1_2"]/h1/text()').extract_first()
        if title is None:
            return
        item["title"] = title
        item["sourceUrl"] = response.url
        # 修改了text_list
        text_list = response.xpath('//div[@class="left_zw"]/p')
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
