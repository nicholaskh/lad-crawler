#coding=utf-8
import scrapy

from lad.items import LadItem

class newsSpider(scrapy.Spider):
    name = "jiangsu"
    start_urls = ['http://www.jsga.gov.cn/jwzx/aqff/index.html']
    text = ""

    def parse(self, response):
        if len(response.xpath('/html/body/div[3]/div/div/div/div[3]/div/table/tbody/tr/td/div/a')) == 15:
            #判断是否是最后一页,不是的话执行下面逻辑
            if len(response.url) == 43:
                next_url = "http://www.jsga.gov.cn/jwzx/aqff/index_2.html"
            else:
                num = int(response.url.split('index')[1][1])
                next_url_part = "index_" + str(num + 1) + ".html"
                next_url = "http://www.jsga.gov.cn/jwzx/aqff/" + next_url_part
            yield scrapy.Request(url=next_url, callback=self.parse)

        for infoDiv in response.xpath('/html/body/div[3]/div/div/div/div[3]/div/table/tbody/tr/td/div/a/@href'):
            info_url = infoDiv.extract()
            n_url = "http://www.jsga.gov.cn" + info_url
            yield scrapy.Request(url=n_url, callback=self.parse_info)

    def parse_info(self, response):
        item = LadItem()

        item["city"] = "江苏"
        item["news_type"] = "公众防范"
        item["title"] = response.xpath('//*[@id="ArticleCnt"]/div[1]/p[3]/span/text()').extract_first()
        item["time"] = response.xpath('/html/body/div[3]/div/div/div/div[3]/div[1]/text()[1]').extract_first().strip()[5:15]

        text_list = response.xpath('//*[@id="ArticleCnt"]/div[1]/p[3]/span/span/span/text()')
        if len(text_list) == 0:
            text_list = response.xpath('//*[@id="ArticleCnt"]/div[1]/p[3]/span/span/text()')
        if len(text_list) == 0:
            text_list = response.xpath('//*[@id="ArticleCnt"]/div[1]/p/span/text()')
        if len(text_list) == 0:
            text_list = response.xpath('//*[@id="ArticleCnt"]/div[1]/p/text()')

        for str_slt in text_list:
            if str_slt.extract() is None:
                self.text = self.text
            else:
                self.text = self.text + str_slt.extract()
        item["text"] = self.text
        self.text = ""

        yield item
