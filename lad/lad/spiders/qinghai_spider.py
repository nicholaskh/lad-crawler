#coding=utf-8
import scrapy

from lad.items import LadItem

class newsSpider(scrapy.Spider):
    name = "qinghai"
    districts = ['Category_115', 'Category_111']
    start_urls = ['http://www.qhga.gov.cn/%s/Index.aspx' % x for x in districts]
    text = ""

    def parse(self, response):

        for infoDiv in response.xpath('/html/body/div/div[2]/div[1]/div/ul/li'):
            info_url = infoDiv.xpath('a/@href').extract_first()
            if info_url is None:
                continue
            else:
                n_url = 'http://www.qhga.gov.cn' + info_url
            yield scrapy.Request(url=n_url, callback=self.parse_info)

    def parse_info(self, response):
        item = LadItem()

        item["city"] = "青海"
        item["newsType"] = response.xpath('/html/body/div/div[2]/div[1]/p/a[3]/text()').extract_first()
        item["title"] = response.xpath('/html/body/div/div[2]/div[2]/h1/text()').extract_first()
        item["time"] = response.xpath('/html/body/div/div[2]/div[2]/div[1]/span[4]/text()').extract_first()[5:16]

        text_list = response.xpath('//*[@id="fontzoom"]/p/span')

        if len(text_list) >= 2:
            for str_slt in text_list:
                if str_slt.xpath('text()').extract_first() is None:
                    self.text = self.text
                else:
                    self.text = self.text + str_slt.xpath('text()').extract_first()
            item["text"] = self.text
        else:
            if text_list.xpath('text()').extract_first() is None:
                self.text = self.text
            else:
                self.text = self.text + text_list.xpath('text()').extract_first()
        self.text = ""

        yield item
