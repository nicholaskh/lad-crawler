#coding=utf-8
import scrapy

from lad.items import LadItem

class newsSpider(scrapy.Spider):
    name = "xizang"
    start_urls = ['http://www.xzgat.gov.cn/jqtx/index.jhtml']
    text = ""

    def parse(self, response):
        if len(response.xpath('//*[@id="container"]/div/div[2]/div/ul/li')) == 20:
            #判断是否是最后一页,不是的话执行下面逻辑
            if len(response.url) <= 40:
                next_url = "http://www.xzgat.gov.cn/jqtx/index_2.jhtml"
            else:
                num = int(response.url.split('_')[1][0]) + 1
                next_url = response.url.split('_')[0] + "_" + '%s' %num + ".jhtml"
            yield scrapy.Request(url=next_url, callback=self.parse)

        for infoDiv in response.xpath('//*[@id="container"]/div/div[2]/div/ul/li'):
            n_url = infoDiv.xpath('a/@href').extract_first()
            yield scrapy.Request(url=n_url, callback=self.parse_info)

    def parse_info(self, response):
        item = LadItem()

        item["city"] = "西藏"
        item["title"] = response.xpath('//*[@id="container"]/div[2]/div/div/div[2]/div[1]/h1/text()').extract_first()
        if response.xpath('//*[@id="container"]/div[2]/div/div/div[2]/div[2]/span[2]/text()') is None:
            item["time"] = response.xpath('//*[@id="container"]/div[2]/div/div/div/div[2]/div[2]/span[2]/text()').extract_first().split(' ')[0][5:15]
        else:
            item["time"] = response.xpath('//*[@id="container"]/div[2]/div/div/div[2]/div[2]/span[2]/text()').extract_first().split(' ')[0][5:15]

        text_list = response.xpath('//*[@id="container"]/div[2]/div/div/div[3]/p/span')

        for str_slt in text_list:
            if str_slt.xpath('text()').extract_first() is None:
                self.text = self.text
            else:
                self.text = self.text + str_slt.xpath('text()').extract_first()
        item["text"] = self.text
        self.text = ""

        yield item
