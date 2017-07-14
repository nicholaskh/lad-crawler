#coding=utf-8
import scrapy

from lad.items import YangshengItem

class newsSpider(scrapy.Spider):
    name = "zhonghuayangsheng"
    start_urls = ['http://www.cnys.com/yscs/index.html']
    text = ""

    def parse(self, response):
        if len(response.url) == 35:
            next_url = 'http://www.cnys.com/yscs/2.html'
            yield scrapy.Request(url=next_url, callback=self.parse)
        else:
            num = int(response.url.split('/')[4].split('.')[0])
            if num < int(response.xpath('/html/body/div/div/div/div/a')[-1].xpath('@href').extract_first().split('.')[0]):
                next_url = "http://www.cnys.com/yscs/" + str(num + 1) + ".html"
                yield scrapy.Request(url=next_url, callback=self.parse)

        for infoDiv in response.xpath('/html/body/div/div/div/ul/li/a/@href'):
            if infoDiv.extract is None:
                continue
            else:
                n_url = infoDiv.extract
                yield scrapy.Request(url=n_url, callback=self.parse_info)

    def parse_info(self, response):
        item = YangshengItem()

        item["web" = "中华养生网"
        item["title"] = response.xpath('/html/body/div/div/div/h1/text()').extract_first()
        item["time"] = response.xpath('/html/body/div/div/div/div[2]/text()').extract_first()[0:9]

        def parse_text(self, response):
            if response.xpath('/html/body/div/div/div/div/a')[-1].xpath('@href').extract_first() is None:
                text_list = response.xpath('/html/body/div/div/div/div/p/text()')
                for p_slt in text_list:
                    if p_slt.extract() is None:
                        self.text = self.text
                    else:
                        self.text = self.text + p_slt.extract()
            else:
                next_url_req = response.xpath('/html/body/div/div/div/div/a')[-1].xpath('@href').extract_first()
                text_list = response.xpath('/html/body/div/div/div/div/p/text()')
                for p_slt in text_list:
                    if p_slt.extract() is None:
                        self.text = self.text
                    else:
                        self.text = self.text + p_slt.extract()
                yield scrapy.Request(url=next_url_req, callback=self.parse_text)
        item["text"] = self.text

        yield item
