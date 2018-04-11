#coding=utf-8
import scrapy
import json
import re
from ..items import DailyNewsItem
from ..spiders.beautifulSoup import processText, processImgSep
from datetime import datetime
from .basespider import BaseTimeCheckSpider

class newsSpider(BaseTimeCheckSpider):
    name = "huanqiuwang_3"
    start_urls = ['http://run.huanqiu.com/control/258/0/10?callback=']

    def parse(self, response):
        data = json.loads(response.text.strip('(').strip(')'))
        pages = data["results"][0]
        for page in pages:
            req = scrapy.Request(url="http://run.huanqiu.com" + page["url"], callback=self.parse_info)
            m_item = DailyNewsItem()
            m_item['className'] = "体育"
            # 相当于在request中加入了item这个元素
            req.meta['item'] = m_item
            yield req

    def parse_info(self, response):
        item = response.meta['item']
        time = re.findall('"publish" : "(.*?)"', response.text)[0]
        try:
            time_now = datetime.fromtimestamp(int(time))
            self.update_last_time(time_now)
        except:
            print("Something Wrong")
            return

        if self.last_time is not None and self.last_time >= time_now:
            return
        item["source"] = "环球网"
        title = response.xpath('//h1[@class="title"]/text()').extract_first()
        if title is None:
            return
        item["time"] = time_now.strftime('%Y-%m-%d')
        item["title"] = title
        item["sourceUrl"] = response.url
        text_list = response.xpath('//div[@class="content"]/*')
        text = processText(text_list)
        item["text"] = text
        img_list = processImgSep(text_list)
        final_img_list = []
        for img in img_list:
            if 'http' not in img:
                img = "http:" + img
            final_img_list.append(img)
        item['imageUrls'] = final_img_list
        if text.strip().replace("$#$", "") == "":
            return
        yield item

