#coding=utf-8
import scrapy

from lad.items import LadItem

class newsSpider(scrapy.Spider):
    name = "sichuan"
    start_urls = ['http://www.scga.gov.cn/jwzx/gdjx/index.html']
    text = ""
    flag = 0

    def parse(self, response):
        if response.xpath('/html/body/div[4]/div[1]/ul/li')[19].xpath('span/text()').extract_first() != '2015-07-02':
            #判断是否是最后一页,不是的话执行下面逻辑
            if len(response.url) == 43:
                next_url = "http://www.scga.gov.cn/jwzx/gdjx/index_1.html"
            else:
                part_str = response.url.split('/')[5]
                num = int(part_str[6])
                next_url_part = "index_" + str(num + 1) + ".html"
                next_url = "http://www.scga.gov.cn/jwzx/gdjx/" + next_url_part
            yield scrapy.Request(url=next_url, callback=self.parse)

        for infoDiv in response.xpath('/html/body/div[4]/div[1]/ul/li/a'):
            part_url = infoDiv.xpath('@href').extract_first()
            url_leng = len(part_url)
            part_url_sec = part_url[1:url_leng]
            n_url = 'http://www.scga.gov.cn/jwzx/gdjx' + part_url_sec
            yield scrapy.Request(url=n_url, callback=self.parse_info)

    def parse_info(self, response):
        item = LadItem()

        item["city"] = "四川"
        item["newsType"] = "各地警讯"
        item["title"] = response.xpath('/html/body/div[4]/div[1]/div/div[1]/text()').extract_first()
        item["time"] = response.xpath('/html/body/div[4]/div[1]/div/table[1]/tr/td[2]/text()').extract_first()

        text_list = response.xapth('//*[@id="Zoom"]/div[1]/div/div/p/font/font/font/font/font/span')
        if len(text_list) == 0:
            text_list = response.xpath('//*[@id="Zoom"]/div[1]/div/div/p/font/font/font/font/span')
        if len(text_list) == 0:
            text_list = response.xpath('//*[@id="Zoom"]/div[1]/div/div/p/font/font/font/span')
        if len(text_list) == 0:
            text_list = response.xpath('//*[@id="Zoom"]/div[1]/div/div/p/font/font/span')
        if len(text_list) == 0:
            text_list = response.xpath('//*[@id="Zoom"]/div[1]/div/div/p/span')
        if len(text_list) == 0:
            text_list = response.xpath('//*[@id="Zoom"]/div[1]/div/p/font')

        for str_slt in text_list:
            if str_slt.xpath('text()').extract_first() is None:
                self.text = self.text
            else:
                self.text = self.text + str_slt.xpath('text()').extract_first()
        item["text"] = self.text
        self.text = ""

        yield item
