#coding=utf-8
import scrapy
import json

from ..items import LadItem
from ..spiders.beautifulSoup import processText, processImgSep
from datetime import datetime
from .basespider import BaseTimeCheckSpider

class newsSpider(BaseTimeCheckSpider):
    name = "changsha_new"
    start_urls = ['http://www.hncsga.gov.cn/webjjcluster/get_articile_info_list.jsp?article_title=&group_sid=11&page=1&rows=15&totalSize=-1']

    def parse(self, response):
        should_deep = True
        data = json.loads(response.text.strip())
        if len(data["rows"]) == 0:
            return
        times = []
        urls = []
        for row in data["rows"]:
            times.append(row["putoudate"])
            url = "http://www.hncsga.gov.cn/webjjcluster/artcledetail.jsp?article_sid=" + row["article_sid"] + "&group_sid=11"
            urls.append(url)

        for time, url in zip(times, urls):
            try:
                time_now = datetime.strptime(time, '%Y-%m-%d')
                self.update_last_time(time_now)
            except:
                print("Something Wrong")
                break

            if self.last_time is not None and self.last_time >= time_now:
                should_deep = False
                break

        next_requests = list()
        if should_deep:
            page_num = int(response.url.rsplit('&', 3)[1].split('=')[1]) + 1
            next_url = "http://www.hncsga.gov.cn/webjjcluster/get_articile_info_list.jsp?article_title=&group_sid=11&page=" + str(page_num) + "&rows=15&totalSize=-1"
            next_requests.append(scrapy.Request(url=next_url, callback=self.parse))

        for index, temp_url in enumerate(urls):
            req = scrapy.Request(url=temp_url, callback=self.parse_info)

            hit_time = times[index]
            m_item = LadItem()
            m_item['time'] = hit_time
            m_item['newsType'] = "警事要闻"
            # 相当于在request中加入了item这个元素
            req.meta['item'] = m_item
            next_requests.append(req)

        for req in next_requests:
            yield req

    def parse_info(self, response):
        item = response.meta['item']

        item["city"] = "长沙公安网"
        title = response.xpath('//td[@class="cssjny_xxdbt"]/text()').extract_first()
        if title is None:
            return
        item["title"] = title
        item["sourceUrl"] = response.url
        # 修改了text_list
        text_list = response.xpath('//td[@class="cssjny_xxxx"]/*')
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
