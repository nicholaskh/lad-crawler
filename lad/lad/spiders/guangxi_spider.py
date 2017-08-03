#coding=utf-8
import scrapy

from lad.items import LadItem

class newsSpider(scrapy.Spider):
    name = "guangxi"
    districts = ['report', 'alert']
    start_urls = ['http://www.gazx.gov.cn/gxgat/%s/index.jhtml' % x for x in districts]
    text = ""

    def parse(self, response):
        if len(response.xpath('/html/body/div[3]/div[2]/div[2]/div/div[1]/div')) == 20:
            #判断是否是最后一页,不是的话执行下面逻辑
            if len(response.url) <= 47:
                next_url = response.url.split('index')[0] + 'index_2.jhtml'
            else:
                num_part = response.url.split('/')[5]
                num = int(num_part[6])
                next_url_part = "index_" + str(num + 1) + ".jhtml"
                next_url = response.url.split('index')[0] + next_url_part
            yield scrapy.Request(url=next_url, callback=self.parse)

        for infoDiv in response.xpath('/html/body/div[3]/div[2]/div[2]/div/div[1]/div/div[1]/a[2]'):
            info_url = infoDiv.xpath('@href').extract_first()
            n_url = "http://www.gazx.gov.cn" + info_url
            yield scrapy.Request(url=n_url, callback=self.parse_info)

    def parse_info(self, response):
        item = LadItem()

        item["city"] = "广西"
        if response.url.split('/')[4] == 'report':
            item["newsType"] = "警情通报"
        else:
            item["newsType"] = "警方提示"
        item["title"] = response.xpath('/html/body/div[3]/div[2]/div[2]/div[1]/text()').extract_first()
        item["time"] = response.xpath('/html/body/div[3]/div[2]/div[2]/div[2]/text()[1]').extract_first().strip()[0:10]

        text_list = response.xpath('/html/body/div[3]/div[2]/div[2]/div[3]/p/span/span/span')
        if len(text_list) == 0:
            text_list = response.xpath('/html/body/div[3]/div[2]/div[2]/div[3]/h1/span')
        if len(text_list) == 0:
            text_list = response.xpath('/html/body/div[3]/div[2]/div[2]/div[3]/p/span')
        if len(text_list) == 0:
            text_list = response.xpath('/html/body/div[3]/div[2]/div[2]/div[3]/div/span')

        for str_slt in text_list:
            if str_slt.xpath('text()').extract_first() is None:
                self.text = self.text
            else:
                self.text = self.text + str_slt.xpath('text()').extract_first()
        item["text"] = self.text
        self.text = ""

        yield item
