#coding=utf-8
import scrapy
import json

from ..items import DailyNewsItem
from ..spiders.beautifulSoup import processText, processImgSep
from datetime import datetime
from .basespider import BaseTimeCheckSpider

class newsSpider(BaseTimeCheckSpider):
    name = "huanqiuwang_2"
    dict_commens = {
        'http://huanqiu.13322ty.com/huanqiu/lanqiu?pageNo=1&pageSize=30': '体育',
        'http://huanqiu.13322ty.com/huanqiu/zuqiu?pageNo=1&pageSize=30': '体育'
    }
    start_urls = ['%s' % x for x in dict_commens.keys()]

    def parse(self, response):
        data = json.loads(response.text.strip())
        print("zagaodea********")
        pages = data["list"]
        for page in pages:
            if page["infoType"] != 1:
                continue
            req = scrapy.Request(url=page["templateUrl"], callback=self.parse_info)
            m_item = DailyNewsItem()
            class_name = "体育"
            m_item['className'] = class_name
            # 相当于在request中加入了item这个元素
            req.meta['item'] = m_item
            yield req

    def parse_info(self, response):
        item = response.meta['item']
        time = response.xpath('//div[@class="time_text"]/text()').extract_first().split(' ')[0].split(u'：')[1]
        try:
            time_now = datetime.strptime(time.split(' ')[0], '%Y-%m-%d')
            self.update_last_time(time_now)
        except:
            print("Something Wrong")
            return

        if self.last_time is not None and self.last_time >= time_now:
            return
        item["source"] = "环球网"
        title = response.xpath('//div[@class="qm_list_main"]/h2/text()').extract_first()
        if title is None:
            return
        item["title"] = title
        item["sourceUrl"] = response.url
        text_list = response.xpath('//div[@class="detail_main"]/p')
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

