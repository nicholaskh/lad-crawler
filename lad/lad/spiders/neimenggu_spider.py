#coding=utf-8
import scrapy

from lad.items import LadItem

class newsSpider(scrapy.Spider):
    name = "neimenggu"
    start_urls = ['http://www.nmgat.gov.cn/jwzx/afgl/index.html']
    text = ""

    def parse(self, response):
        if len(response.xpath('/html/body/div/div/div[2]/div[3]/div[2]/div[2]/div[2]/ul/li')) == 30:
            #判断是否是最后一页,不是的话执行下面逻辑
            if len(response.url) == 44:
                next_url = 'http://www.nmgat.gov.cn/jwzx/afgl/index_1.html'
            else:
                part_str = response.url.split('/')[5]
                num = int(part_str[6])
                next_url_part = "index_" + str(num + 1) + ".html"
                next_url = 'http://www.nmgat.gov.cn/jwzx/afgl/' + next_url_part
            yield scrapy.Request(url=next_url, callback=self.parse)

        for infoDiv in response.xpath('/html/body/div/div/div[2]/div[3]/div[2]/div[2]/div[2]/ul/li'):
            info_url_part = infoDiv.xpath('a/@href').extract_first()
            arry_leng = len(info_url_part.split('/'))
            info_url_sec = info_url_part.split('/')[(arry_leng-2) : arry_leng]
            info_url = info_url_sec[0] + '/' + info_url_sec[1]
            n_url = 'http://www.nmgat.gov.cn/jwzx/afgl/' + info_url
            yield scrapy.Request(url=n_url, callback=self.parse_info)

    def parse_info(self, response):
        item = LadItem()

        item["newsType"] = '警事要闻'
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
