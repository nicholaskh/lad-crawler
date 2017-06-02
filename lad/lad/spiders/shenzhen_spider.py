#coding=utf-8
import scrapy

from lad.items import LadItem

class newsSpider(scrapy.Spider):
    name = "shenzhen"
    start_urls = ["http://www.szga.gov.cn/JFZX/JFTS/FD/"]
    time = 0
    num = 0
    text = ""

    def parse(self, response):
        if len(response.xpath('/html/body/div/div[1]/div[4]/div[2]/ul/li')) == 16:
            next_url_part = "/index_" + str(self.time + 1) + ".html"
            next_url = 'http://www.szga.gov.cn/JFZX/JFTS/FD' + next_url_part
            self.time = self.time + 1
            yield scrapy.Request(url=next_url, callback=self.parse)

        for infoDiv in response.xpath('/html/body/div/div[1]/div[4]/div[2]/ul/li')[1:15]:
            info_url = infoDiv.extract().encode('utf-8').split('.')[1]
            n_url = 'http://www.szga.gov.cn/JFZX/JFTS/FD' + info_url + ".html"
            yield scrapy.Request(url=n_url, callback=self.parse_info)

    def parse_info(self, response):
        item = LadItem()

        item["title"] = response.xpath('/html/body/div/div[1]/div[4]/div[1]/h4/text()').extract()[0].encode('utf-8')
        item["time"] = response.xpath('/html/body/div/div[1]/div[4]/div[1]/div/p[2]/text()').extract_first().encode('utf-8').split('：')[1]        #rows = list(array)

        text_list = response.xpath('//*[@id="txtContent"]/div/div/div/p')
        flag = 0
        if len(text_list) == 0:
            text_list = response.xpath('//*[@id="txtContent"]/div/p/span')
            flag = 1
        if flag == 0:
            for str_slt in text_list:
                if str_slt.xpath('text()').extract_first() is None:
                    self.text = self.text
                else:
                    self.text = self.text + str_slt.xpath('text()').extract_first()
        elif flag == 1:
            for sp_str in text_list:
                self.text = self.text + sp_slt.xpath('text()').extract_first()
        item["text"] = self.text

        yield item
