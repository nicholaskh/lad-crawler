#coding=utf-8
import scrapy
import re

from ..items import DailyNewsItem
from ..spiders.beautifulSoup import processText, processImgSep
from datetime import datetime
from .basespider import BaseTimeCheckSpider

class newsSpider(BaseTimeCheckSpider):
    name = "xinhuawang_guoji6"
    start_urls = ['http://my.xinhuanet.com/zx/zy.htm',
                  'http://my.xinhuanet.com/zx/dmyw.htm',
                  'http://my.xinhuanet.com/zx/mlxyhr.htm',
                  'http://my.xinhuanet.com/zx/zmgx.htm',
                  'http://my.xinhuanet.com/cj/dmtz.htm',
                  'http://my.xinhuanet.com/cj/dmcj.htm',
                  'http://my.xinhuanet.com/cj/qy.htm',
                  'http://my.xinhuanet.com/pl/xhsjz.htm',
                  'http://my.xinhuanet.com/pl/mtpl.htm',
                  'http://my.xinhuanet.com/jy/index.htm']

    def parse(self, response):
        urls = response.xpath('//div[@class="news-list"]/ul/li/a/@href').extract()
        valid_child_urls = list()
        times = list()

        for url in urls:
            time = time = url.rsplit('/', 3)[-3] + "-" + url.rsplit('/', 3)[-2]
            try:
                time_now = datetime.strptime(time, '%Y-%m-%d')
                self.update_last_time(time_now)
                times.append(time)
            except:
                print("error time format")
                continue

            if self.last_time is not None and self.last_time >= time_now:
                continue
            valid_child_urls.append(url)

        for index, temp_url in enumerate(valid_child_urls):
            req = scrapy.Request(url=temp_url, callback=self.parse_info)

            hit_time = times[index]
            m_item = DailyNewsItem()
            m_item['time'] = hit_time
            m_item['className'] = "国际"
            # 相当于在request中加入了item这个元素
            req.meta['item'] = m_item
            yield req

    def parse_info(self, response):
        item = response.meta['item']
        item["source"] = "新华网"

        title = response.xpath('//div[@class="detail-title"]/h1/text() | //div[@class="h-title"]').extract_first()
        if title is None:
            return
        item["title"] = title
        item["sourceUrl"] = response.url
        # 修改了text_list
        text_list = response.xpath('//div[@class="detail-content"]/p | //div[@id="p-detail"]/p')
        text = processText(text_list)
        item["text"] = text
        img_list = processImgSep(text_list)
        final_img_list = []
        for img in img_list:
            if 'http' not in img:
                img = response.url.rsplit('/', 1)[0] + '/' + img
            final_img_list.append(img)
        item['imageUrls'] = final_img_list
        if text.strip().replace("$#$", "") == "":
            return

        yield item
