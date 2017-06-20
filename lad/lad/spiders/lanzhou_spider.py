#coding=utf-8
import scrapy

from lad.items import LadItem

class newsSpider(scrapy.Spider):
    name = "lanzhou"
    districts = ['jcjx', 'mt', 'xwfb']
    start_urls = ['http://www.lzsgaj.gov.cn/gaxw/%s/index.shtml' % x for x in districts]
    text = ""

    def parse(self, response):
        if len(response.xpath('//*[@id="mid"]/ul/li')) == 20:
            #判断是否是最后一页,不是的话执行下面逻辑
            if len(response.url) == 46 or len(response.url) == 44:
                next_url = response.url.split('index')[0] + "index_2.shtml"
            else:
                part_str = response.url.split('/')[5]
                num = int(part_str[6])
                next_url_part = "index_" + str(num + 1) + ".shtml"
                next_url = response.url.split('index')[0] + next_url_part
            yield scrapy.Request(url=next_url, callback=self.parse)

        for infoDiv in response.xpath('//*[@id="mid"]/ul/li'):
            info_url = infoDiv.xpath('a/@href').extract_first().split('..')[2]
            n_url = 'http://www.lzsgaj.gov.cn' + info_url
            yield scrapy.Request(url=n_url, callback=self.parse_info)

    def parse_info(self, response):
        item = LadItem()

        item["city"] = "兰州"
        item["news_type"] = response.url.split('/')[4]
        item["title"] = response.xpath('//*[@id="mid"]/div[2]/h1/font/text()').extract_first()
        item["time"] = response.xpath('//*[@id="mid"]/div[2]/div[1]/text()[1]').extract_first().strip()[5:15]

        text_list = response.xpath('//*[@id="content"]/p/span/span/span/font')
        if text_list == 0:
            text_list = response.xpath('//*[@id="content"]/p/span/span/span/span')
        if len(text_list) == 0:
            text_list = response.xpath('//*[@id="content"]/p/span/span/span')
        if len(text_list) == 0:
            text_list = response.xpath('//*[@id="content"]/div/span/span/span')
        if len(text_list) == 0:
            text_list = response.xpath('//*[@id="content"]/p/font')
        if len(text_list) == 0:
            text_list = response.xpath('//*[@id="content"]/p/span')
        if len(text_list) == 0:
            text_list = response.xpath('//*[@id="content"]/div/span')
        if len(text_list) == 0:
            text_list = response.xpath('//*[@id="content"]/p')

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
