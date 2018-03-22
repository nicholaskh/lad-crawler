#coding=utf-8
import scrapy
import re

from ..items import LadItem
from ..spiders.beautifulSoup import processText, processImgSep
from datetime import datetime
from .basespider import BaseTimeCheckSpider

class newsSpider(BaseTimeCheckSpider):
    name = "hubei_new"
    start_urls = ['http://www.hbgat.gov.cn/info/iList.jsp?site_id=HIWCMhbgat&cat_id=2697&cur_page=1']

    def parse(self, response):
        should_deep = True
        times = response.xpath('//ul[@class="list-b-t"]//li/p/text()').extract()
        #相对链接
        urls = response.xpath('//ul[@class="list-b-t"]//li/h4/a/@href').extract()

        valid_child_urls = list()

        for time, url in zip(times, urls):
            try:
                time_now = datetime.strptime(time.split(u'：')[1].split(u'　　')[0], '%Y-%m-%d')
                self.update_last_time(time_now)
            except:
                print("Something Wrong")
                break

            if self.last_time is not None and self.last_time >= time_now:
                should_deep = False
                break
            url = "http://www.hbgat.gov.cn" + url
            valid_child_urls.append(url)

        next_requests = list()
        if should_deep:
            page_num = int(response.url.rsplit('=', 1)[-1])
            all_page = response.xpath('//p[@class="pages"]/a[4]/@href').extract_first().rsplit('=', 1)[-1]
            if all_page is not None and int(all_page) > page_num:
                next_page = page_num + 1
                next_url = response.url.rsplit('=', 1)[0] + "=" + str(next_page)
                next_requests.append(scrapy.Request(url=next_url, callback=self.parse))

        for index, temp_url in enumerate(valid_child_urls):
            req = scrapy.Request(url=temp_url, callback=self.parse_info)

            hit_time = times[index]
            m_item = LadItem()
            m_item['time'] = hit_time.split(u'：')[1].split(u'　　')[0]
            m_item['newsType'] = "警事要闻"
            # 相当于在request中加入了item这个元素
            req.meta['item'] = m_item
            next_requests.append(req)

        for req in next_requests:
            yield req

    def parse_info(self, response):
        item = response.meta['item']

        item["city"] = "湖北公安网"
        title = response.xpath('//h2[@class="tc"]/text()').extract_first()
        if title is None:
            return
        item["title"] = title
        item["sourceUrl"] = response.url
        # 修改了text_list
        text_list = response.xpath('//div[@class="article-box"]/text() | //div[@class="article-box"]/*')
        text = processText(text_list)
        item["text"] = text
        img_list = processImgSep(text_list)
        final_img_list = []
        for img in img_list:
            if 'http' in img:
                final_img_list.append(img)
        item['imageUrls'] = final_img_list
        if text.strip() == "" and len(img_list) == 0:
            return

        yield item
