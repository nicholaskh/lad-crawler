#coding=utf-8
import scrapy
import re

from ..items import DailyNewsItem
from ..spiders.beautifulSoup import processText, processImgSep


class newsSpider(scrapy.Spider):
    name = "renminwang_zhengzhi2"
    start_urls = ['http://politics.people.com.cn/GB/385431/index1.html', 'http://politics.people.com.cn/GB/385431/index2.html', 'http://politics.people.com.cn/GB/385431/index3.html']

    def parse(self, response):
        times = response.xpath('//ul[@id="tiles"]/li/div/em/text()[2]').extract()
        #格式不规范
        urls = response.xpath('//ul[@id="tiles"]/li//h4/a/@href').extract()

        for time, url in zip(times, urls):
            # 变成绝对url
            url = "http://politics.people.com.cn" + url
            time = time.strip().strip(u'（').split(' ')[0]
            req = scrapy.Request(url=url, callback=self.parse_info)
            m_item = DailyNewsItem()
            m_item['time'] = time
            m_item['className'] = "政治"
            # 相当于在request中加入了item这个元素
            req.meta['item'] = m_item
            yield req

    def parse_info(self, response):
        item = response.meta['item']
        item["source"] = "人民网"

        title = response.xpath('//div[@class="clearfix w1000_320 text_title"]/h1/text()').extract_first()
        if title is None:
            return
        item["title"] = title
        item["sourceUrl"] = response.url
        # 修改了text_list
        text_list = response.xpath('//div[@class="box_con"]//p | //div[@class="box_con"]//img')
        text = processText(text_list)
        item["text"] = text
        img_list = processImgSep(text_list)
        final_img_list = []
        for img in img_list:
            if 'http' not in img:
                img = "http://politics.people.com.cn" + img
            final_img_list.append(img)
        item['imageUrls'] = final_img_list
        if text.strip().replace("$#$", "") == "":
            return

        yield item
