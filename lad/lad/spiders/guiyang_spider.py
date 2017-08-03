#coding=utf-8
import scrapy

from lad.items import LadItem

class newsSpider(scrapy.Spider):
    name = "guiyang"
    start_urls = ['http://www.gyga.gov.cn/templet/gyga/ShowClass.jsp?id=gyjx']
    text = ""

    def parse(self, response):
        if len(response.xpath('//*[@id="List"]/div/ul/li')) == 7:
            #判断是否是最后一页,不是的话执行下面逻辑
            if len(response.url) == 57:
                next_url = 'http://www.gyga.gov.cn/templet/gyga/ShowClass.jsp?id=gyjx&pn=2'
            else:
                num = int(response.url.split('=')[2]) + 1
                next_url = 'http://www.gyga.gov.cn/templet/gyga/ShowClass.jsp?id=gyjx&pn=' + str(num)
            yield scrapy.Request(url=next_url, callback=self.parse)

        for infoDiv in response.xpath('//*[@id="List"]/div/ul/li'):
            info_url = infoDiv.xpath('a/@href').extract_first()
            n_url = info_url
            yield scrapy.Request(url=n_url, callback=self.parse_info)

    def parse_info(self, response):
        item = LadItem()

        item["newsType"] = '警方提示'
        item["title"] = response.xpath('/html/body/div/div/div[2]/div[3]/div/div/div[2]/text()').extract_first()
        item["time"] = response.xpath('/html/body/div/div/div[2]/div[3]/div/div/div[3]/div[2]/text()').extract_first().split('|')[1].strip()

        text_list = response.xpath('/html/body/div/div/div[2]/div[3]/div/div/div[4]/div[1]/div/div/div/p/font')
        if len(text_list) == 0:
            text_list = response.xpath('/html/body/div/div/div[2]/div[3]/div/div/div[4]/div[1]/div/div/p')
        if len(text_list) == 0:
            text_list = response.xpath('/html/body/div/div/div[2]/div[3]/div/div/div[4]/div[1]/div/div/span')
        if len(text_list) == 0:
            text_list = response.xpath('/html/body/div/div/div[2]/div[3]/div/div/div[4]/div[1]/div/div')
        if len(text_list) == 0:
            text_list = response.xpath('/html/body/div/div/div[2]/div[3]/div/div/div[4]/div[1]/div/p/span')
        if len(text_list) == 0:
            text_list = response.xpath('/html/body/div/div/div[2]/div[3]/div/div/div[4]/div[1]/div/span')

        if len(text_list) >= 2:
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
