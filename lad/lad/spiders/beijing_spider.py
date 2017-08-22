#coding=utf-8
import scrapy
import re

from lad.items import LadItem

class newsSpider(scrapy.Spider):
    name = "beijing"
    start_urls = ['http://www.bjgaj.gov.cn/web/xwpd_zfts.html']
    text = ""

    def parse(self, response):
        if len(response.xpath('//*[@id="yun1"]/tr')) == 31:
            #判断是否是最后一页,不是的话执行下面逻辑
            if len(response.url) <= 42:
                next_url = 'http://www.bjgaj.gov.cn/web/listPage_allJfts_col1167_30_2.html'
            else:
                num = int(response.url[56])
                next_url = response.url[0:56] + str(num + 1) + ".html"
            yield scrapy.Request(url=next_url, callback=self.parse)

        for infoDiv in response.xpath('//*[@id="yun1"]/tr'):
            if infoDiv.xpath('td/a/@href').extract_first() is None:
                continue
            else:
                n_url = "http://www.bjgaj.gov.cn" + infoDiv.xpath('td/a/@href').extract_first()
                self.news_type = response.xpath('//*[@id="yun1"]/tr')[3].xpath('td/span/strong/a/text()').extract_first()
                yield scrapy.Request(url=n_url, callback=self.parse_info)

    def parse_info(self, response):
        item = LadItem()

        item["city"] = "北京"
        item["newsType"] = '警务要闻'
        item["title"] = response.xpath('/html/body/table[3]/tr/td/table[2]/tr/td[3]/table/tr/td/table/tr[2]/td/table/tr[1]/td/font/b/text()').extract_first()
        c = response.xpath('/html/body/table[3]/tr/td/table[2]/tr/td[3]/table/tr/td/table/tr[2]/td/table/tr[2]/td/text()').extract_first().split('www.bjgaj.gov.cn')[1].strip()
        c = re.sub("\D", "", c)
        item["time"] = c[0:4] + '-' + c[4:6] + '-' + c[6:8]

        text_list = response.xpath('//*[@id="articleContent"]/p')

        for p_slt in text_list:
            if p_slt.xpath('text()').extract_first() is None:
                self.text = self.text
            else:
                self.text = self.text + p_slt.xpath('text()').extract_first()
        item["text"] = self.text
        self.text = ""

        yield item
