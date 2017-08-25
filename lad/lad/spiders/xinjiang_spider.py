#coding=utf-8
import scrapy
import re

from lad.items import LadItem
from lad.spiders.beautifulSoup import processText

class newsSpider(scrapy.Spider):
    name = "xinjiang"
    start_urls = ['http://www.xjgat.gov.cn/html/column/1545/index.shtml']
    text = ""
    flag = 1

    def parse(self, response):
        if len(response.xpath('/html/body/div/div[2]/div[2]/div/div[2]/ul/li')) == 45:
            #判断是否是最后一页,不是的话执行下面逻辑
            if len(response.url) == 52:
                next_url = "http://www.xjgat.gov.cn/html/column/1545/index_2.shtml"
            else:
                part_str = response.url.split('/')[6]
                num = int(part_str[6])
                next_url_part = "index_" + str(num + 1) + ".shtml"
                url_len = len(response.url)
                next_url = response.url[0:(url_len) - 13] + next_url_part
            yield scrapy.Request(url=next_url, callback=self.parse)

        for infoDiv in response.xpath('/html/body/div/div[2]/div[2]/div/div[2]/ul/li'):
            info_url = infoDiv.xpath('a/@href').extract_first()
            n_url = "http://www.xjgat.gov.cn" + info_url
            yield scrapy.Request(url=n_url, callback=self.parse_info)

    def parse_info(self, response):
        item = LadItem()

        item["city"] = "新疆"
        item['newsType'] = '警事要闻'
        item["title"] = response.xpath('/html/body/div[1]/div[2]/div[2]/div/div/div[1]/text()').extract_first()
        c = response.xpath('/html/body/div[1]/div[2]/div[2]/div/div/div[2]/text()').extract_first().strip().split(' ')[0]
        c = re.sub("\D", "", c)
        item["time"] = c[0:4] + '-' + c[4:6] + '-' + c[6:8]

        if len(response.xpath('/html/body/div[1]/div[2]/div[2]/div/div/div[2]/text()').extract_first().strip().split(' ')[0]) == 0:
            item["time"] = response.xpath('//*[@id="right"]/div[1]/div[1]/div[1]/text()').extract_first().strip().split(' ')[0]
            item["title"] = response.xpath('//*[@id="right"]/div[1]/div[1]/h3/text()').extract_first()

        text_list = response.xpath('/html/body/div[1]/div[2]/div[2]/div/div/div[5]/p/span')
        if len(text_list) <= 1:
            text_list = response.xpath('/html/body/div[1]/div[2]/div[2]/div/div/div[5]/p/font')
        if len(text_list) <= 1:
            text_list = response.xpath('/html/body/div[1]/div[2]/div[2]/div/div/div[5]/p')
        if len(text_list) <= 1:
            text_list = response.xpath('//*[@id="right"]/div[1]/div[2]/p')
        if len(text_list) <= 1:
            text_list = response.xpath('/html/body/div[1]/div[2]/div[2]/div/div/div[5]/table/tbody/tr/td/p/span')
        if len(text_list) <= 1:
            text_list = response.xpath('/html/body/div[1]/div[2]/div[2]/div/div/div[5]/p/span')
        if len(text_list) <= 1:
            text_list = response.xpath('/html/body/div[1]/div[2]/div[2]/div/div/div[5]/span')
        if len(text_list) > 1:
            for p_list in text_list:
                if p_list.xpath('text()').extract_first() is None:
                    self.text = self.text
                else:
                    self.text = self.text + p_list.xpath('text()').extract_first()
        else:
            self.text = response.xpath('/html/body/div[1]/div[2]/div[2]/div/div/div[5]/span/text()').extract_first()
        item["text"] = self.text
        self.text = ""

        yield item
