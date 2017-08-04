#coding=utf-8
import scrapy

from lad.items import LadItem

class newsSpider(scrapy.Spider):
    name = "jinan"
    start_urls = ['http://www.jnmsjw.gov.cn/channels/209.html']
    text = ""

    def parse(self, response):
        if len(response.xpath('//*[@id="left"]/div/ul/li/a/@href')) == 15:
            #判断是否是最后一页,不是的话执行下面逻辑
            if len(response.url) == 42:
                next_url = 'http://www.jnmsjw.gov.cn/channels/209_2.html'
            else:
                num = int(response.url.split('_')[1][0])
                next_url = 'http://www.jnmsjw.gov.cn/channels/209_' + str(num + 1) + ".html"
            yield scrapy.Request(url=next_url, callback=self.parse)

        for infoDiv in response.xpath('//*[@id="left"]/div/ul/li/a/@href'):
            n_url = "http://www.jnmsjw.gov.cn" + infoDiv.extract()
            yield scrapy.Request(url=n_url, callback=self.parse_info)

    def parse_info(self, response):
        item = LadItem()

        item["city"] = "济南"
        item["newsType"] = "警事要闻"
        item["title"] = response.xpath('//*[@id="content-title"]/h3/text()').extract_first()
        item["time"] = response.xpath('//*[@id="content-title"]/text()').extract()[1].strip()[0:10]

        text_list = response.xpath('//*[@id="content"]/p/span/text()')
        if len(text_list) == 0:
            text_list = response.xpath('//*[@id="content"]/div/div/p/span/text()')
        if len(text_list) == 0:
            text_list = response.xpath('//*[@id="content"]/div/div/div/p/span/text()')

        for p_slt in text_list:
            if p_slt.extract() is None:
                self.text = self.text
            else:
                self.text = self.text + p_slt.extract()
        item["text"] = self.text
        self.text = ""

        yield item
