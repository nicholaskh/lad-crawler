#coding=utf-8
import scrapy

from lad.items import LadItem

class newsSpider(scrapy.Spider):
    name = "zhejiang2"
    start_urls = ['http://www.zjsgat.gov.cn/jwzx/lszt/ztzl/jgsa/']
    text = ""
    flag = 0

    def parse(self, response):
        if len(response.xpath('/html/body/table[6]/tr/td[3]/table[2]/tr[2]/td/table[1]/tr')) == 10:
            #判断是否是最后一页,不是的话执行下面逻辑
            if len(response.url) == 45:
                next_url = "http://www.zjsgat.gov.cn/jwzx/lszt/ztzl/jgsa/index_1.html"
            else:
                num = int(response.url.split('/')[7][6])
                next_url = 'http://www.zjsgat.gov.cn/jwzx/lszt/ztzl/jgsa/index_' + str(num + 1) + ".html"
            yield scrapy.Request(url=next_url, callback=self.parse)

        for infoDiv in response.xpath('/html/body/table[6]/tr/td[3]/table[2]/tr[2]/td/table[1]/tr/td/a/@href'):
            n_url_sec = infoDiv.extract()
            url_leng = len(n_url_sec)
            n_url = 'http://www.zjsgat.gov.cn/jwzx/lszt/ztzl/jgsa' + n_url_sec[1:url_leng]
            yield scrapy.Request(url=n_url, callback=self.parse_info)

    def parse_info(self, response):
        item = LadItem()

        item["city"] = "浙江"
        item["news_type"] = "警官说案"
        item["title"] = response.xpath('/html/body/table[6]/tr/td/table[2]/tr/td/table[2]/tr/td/text()').extract_first()
        time_leng = len(response.xpath('/html/body/table[6]/tr/td/table[2]/tr/td/table[3]/tr/td/table[2]/tr/td/text()').extract_first().strip())
        item["time"] = response.xpath('/html/body/table[6]/tr/td/table[2]/tr/td/table[3]/tr/td/table[2]/tr/td/text()').extract_first().strip()[time_leng - 10:time_leng]

        text_list = response.xpath('/html/body/table[6]/tr/td/table[2]/tr/td/table[3]/tr/td/table[6]/tr/td[1]/div/p/font')
        if len(text_list) == 0:
            text_list = response.xpath('/html/body/table[6]/tr/td/table[2]/tr/td/table[3]/tr/td/table[6]/tr/td[1]/div/p')

        if len(text_list) == 1:
            if text_list.xpath('text()').extract_first() is None:
                self.text = self.text
            else:
                self.text = self.text + text_list.xpath('text()').extract_first()

        for str_slt in text_list:
            if str_slt.xpath('text()').extract_first() is None:
                self.text = self.text
            else:
                self.text = self.text + str_slt.xpath('text()').extract_first()
        item["text"] = self.text
        self.text = ""

        yield item
