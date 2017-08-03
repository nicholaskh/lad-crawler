#coding=utf-8
import scrapy

from lad.items import LadItem

class newsSpider(scrapy.Spider):
    name = "kunming"
    start_urls = ['http://gaj.km.gov.cn/zxdt/jwdt/']
    text = ""

    def parse(self, response):
        if len(response.xpath('/html/body/div[5]/div[2]/div[2]/ul/li')) == 20:
            #判断是否是最后一页,不是的话执行下面逻辑
            if len(response.url) == 31:
                next_url = "http://gaj.km.gov.cn/zxdt/jwdt/index_2.shtml"
            else:
                part_str = response.url.split('/')[5]
                num = int(part_str[6])
                next_url_part = "index_" + str(num + 1) + ".shtml"
                next_url = response.url.split('index')[0] + next_url_part
            yield scrapy.Request(url=next_url, callback=self.parse)

        for infoDiv in response.xpath('/html/body/div[5]/div[2]/div[2]/ul/li'):
            info_url = infoDiv.xpath('a/@href').extract_first()
            n_url = 'http://gaj.km.gov.cn' + info_url
            yield scrapy.Request(url=n_url, callback=self.parse_info)

    def parse_info(self, response):
        item = LadItem()

        item["newsType"] = "警务动态"
        item["title"] = response.xpath('/html/body/div[5]/div[2]/div[2]/h1/text()').extract_first()
        item["time"] = response.xpath('/html/body/div[5]/div[2]/div[2]/div[1]/span[1]/text()').extract_first()

        text_list = response.xpath('/html/body/div[5]/div[2]/div[2]/div[2]/p')

        for str_slt in text_list:
            if str_slt.xpath('text()').extract_first() is None:
                self.text = self.text
            else:
                self.text = self.text + str_slt.xpath('text()').extract_first()
        item["text"] = self.text
        self.text = ""

        yield item
