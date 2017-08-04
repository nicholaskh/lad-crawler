#coding=utf-8
import scrapy

from lad.items import LadItem

class newsSpider(scrapy.Spider):
    name = "hainan"
    start_urls = ['http://ga.hainan.gov.cn/28/']
    text = ""

    def parse(self, response):
        for infoDiv in response.xpath('/html/body/table[2]/tr[2]/td/table/tr/td[3]/table[4]/tr[2]/td/table[3]/tr/td[2]/a'):
            info_url = infoDiv.xpath('@href').extract_first()
            n_url = "http://ga.hainan.gov.cn" + info_url
            yield scrapy.Request(url=n_url, callback=self.parse_info)

    def parse_info(self, response):
        item = LadItem()

        item["city"] = "海南"
        item["newsType"] = "警事要闻"
        item["title"] = response.xpath('//*[@id="artibody"]/table/tr[1]/td/font/text()').extract_first()
        item["time"] = '2015-9-24'

        text_list = response.xpath('//*[@id="artibody"]/table/tr[4]/td')

        if len(text_list) >=2:
            for str_slt in text_list:
                if str_slt.xpath('text()').extract_first() is None:
                    self.text = self.text
                else:
                    self.text = self.text + str_slt.xpath('text()').extract_first()
        else:
            if text_list.xpath('text()').extract_first() is None:
                self.text = self.text
            else:
                self.text = self.text + text_list.xpath('text()').extract_first()
        item["text"] = self.text
        self.text = ""

        yield item
