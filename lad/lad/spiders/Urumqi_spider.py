#coding=utf-8
import scrapy

from lad.items import LadItem

class newsSpider(scrapy.Spider):
    name = "Urumqi"
    districts = ['38614', '38618']
    start_urls = ['http://www.wlsga.gov.cn/html/column/%s/index.shtml' % x for x in districts]
    text = ""

    def parse(self, response):
        if len(response.xpath('/html/body/div[2]/table/tr/td[3]/div[2]/div')) == 26:
            #判断是否是最后一页,不是的话执行下面逻辑
            if len(response.url) == 53:
                next_url_part = "index_2.shtml"
                next_url = response.url.split('index')[0] + next_url_part
            else:
                part_str = response.url.split('/')[6]
                num = int(part_str[6])
                next_url_part = "index_" + str(num + 1) + ".shtml"
                url_len = len(response.url)
                next_url = response.url[0:(url_len) - 13] + next_url_part
            yield scrapy.Request(url=next_url, callback=self.parse)

        for infoDiv in response.xpath('/html/body/div[2]/table/tr/td[3]/div[2]/div'):
            info_url = infoDiv.xpath('div[1]/a/@href').extract_first()
            if info_url is None:
                continue
            else:
                n_url = "http://www.wlsga.gov.cn" + info_url
            if n_url is None:
                continue
            else:
                yield scrapy.Request(url=n_url, callback=self.parse_info)

    def parse_info(self, response):
        item = LadItem()

        item["city"] = "乌鲁木齐"
        item["news_type"] = '警事要闻'
        item["title"] = response.xpath('/html/body/div[2]/table/tr/td[3]/div/div[1]/text()').extract_first()
        item["time"] = response.xpath('/html/body/div[2]/table/tr/td[3]/div/div[2]/text()').extract_first().strip().split(' ')[0]

        text_list = response.xpath('/html/body/div[2]/table/tr/td[3]/div/div[4]/p')
        if len(text_list) == 0:
            text_list = response.xpath('/html/body/div[2]/table/tr/td[3]/div/div[4]/span')
        if len(text_list) == 0:
            text_list = response.xpath('/html/body/div[2]/table/tr/td[3]/div/div[4]/div')
        if len(text_list) == 0:
            text_list = response.xpath('/html/body/div[2]/table/tr/td[3]/div/div[4]/span/font/p')

        for p_list in text_list:
            if len(p_list.xpath('font/span')) == 1:
                self.text = self.text + p_list.xpath('font/span/text()').extract_first()
            elif len(p_list.xpath('font/span')) > 1:
                for span_list in p_list.xpath('font/span'):
                    self.text = self.text + p_list.xpath('font/span/text()').extract_first()
            elif len(p_list.xpath('font/span')) == 0:
                if len(p_list.xpath('font')) > 0:
                    if len(p_list.xpath('font')) == 1:
                        if p_list.xpath('font/text()').extract_first() is None:
                            self.text = self.text
                        else:
                            self.text = self.text + p_list.xpath('font/text()').extract_first()
                elif len(p_list.xpath('span')) > 0:
                    if len(p_list.xpath('span')) == 1:
                        if p_list.xpath('span/text()').extract_first() is None:
                            self.text = self.text
                        else:
                            self.text = self.text + p_list.xpath('span/text()').extract_first()
                    else:
                        for span_list_sec in p_list.xpath('span'):
                            if span_list_sec.xpath('text()').extract_first() is None:
                                self.text = self.text
                            else:
                                self.text = self.text + span_list_sec.xpath('text()').extract_first()
        item["text"] = self.text
        self.text = ""
        yield item
