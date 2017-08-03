#coding=utf-8
import scrapy

from lad.items import LadItem

class newsSpider(scrapy.Spider):
    name = "haikou"
    start_urls = ['http://police.haikou.gov.cn/ycjx/index.htm']
    text = ""

    def parse(self, response):
        if response.xpath('/html/body/table[4]/tr/td/table/tr[2]/td/table[2]/tr/td/table[1]/tr[20]/td[3]/text()').extract_first() != '2010-01-03':
            #判断是否是最后一页,不是的话执行下面逻辑
            if len(response.url) == 42:
                next_url = 'http://police.haikou.gov.cn/ycjx/index_1.htm'
            else:
                num = int(response.url.split('/')[4][6]) + 1
                next_url = 'http://police.haikou.gov.cn/ycjx/index_' + str(num) + '.htm'
            yield scrapy.Request(url=next_url, callback=self.parse)

        for infoDiv in response.xpath('/html/body/table[4]/tr/td/table/tr[2]/td/table[2]/tr/td/table[1]/tr'):
            part_url = infoDiv.xpath('td[2]/a/@href').extract_first()
            url_leng = len(part_url)
            part_url_sec = part_url[1:url_leng]
            n_url = 'http://police.haikou.gov.cn/ycjx' + part_url_sec
            yield scrapy.Request(url=n_url, callback=self.parse_info)

    def parse_info(self, response):
        item = LadItem()

        item["newsType"] = '椰城警讯'
        item["title"] = response.xpath('/html/body/table[4]/tr/td/table/tr[2]/td/table/tr/td/table/tr[1]/td/div/span/text()').extract_first()
        item["time"] = response.xpath('/html/body/table[4]/tr/td/table/tr[2]/td/table/tr/td/table/tr[4]/td/div/text()[2]').extract_first().strip()

        text_list = response.xpath('/html/body/table[4]/tr/td/table/tr[2]/td/table/tr/td/table/tr[4]/td/table[1]/tr[2]/td/span/div/div/div/p')

        if text_list.xpath('text()').extract_first() is None:
            self.text = self.text
        else:
            self.text = self.text + text_list.xpath('text()').extract_first()
        item["text"] = self.text
        self.text = ""

        yield item
