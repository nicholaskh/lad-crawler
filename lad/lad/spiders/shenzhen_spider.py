#coding=utf-8
import scrapy

from lad.items import LadItem

class newsSpider(scrapy.Spider):
    name = "shenzhen"
    districts = ['FH', 'FD', 'FP', 'FSG', 'FQT', 'FQ']
    start_urls = ['http://www.szga.gov.cn/JFZX/JFTS/%s/' % x for x in districts]
    text = ""

    def parse(self, response):
        if len(response.xpath('//*[@class="listnums"]/li/a/@href')) == 15:
            #判断是否是最后一页,不是的话执行下面逻辑
            if len(response.url) < 38:
                next_url_part = "index_" + str(1) + ".htm"
                next_url = response.url + next_url_part
            else:
                part_str = response.url.split('/')[6]
                num = int(part_str[6])
                next_url = response.url.split('_')[0] + '_' + str(num+1) + '.htm'
            yield scrapy.Request(url=next_url, callback=self.parse)

        for infoDiv in response.xpath('//*[@class="listnums"]/li/a/@href').extract():
            info_url = infoDiv.split('./')[1]
            n_url = response.url.split('index')[0] + info_url
            yield scrapy.Request(url=n_url, callback=self.parse_info)

    def parse_info(self, response):
        item = LadItem()

        item["city"] = "深圳"
        typeString = response.url.split('/')[5]
        if typeString == 'FH':
            item["newsType"] = '防火'
        if typeString == 'FD':
            item["newsType"] = '防盗'
        if typeString =='FP':
            item["newsType"] = '防骗'
        if typeString == 'FSG':
            item["newsType"] = '防事故'
        if typeString == 'FQ':
            item["newsType"] = '防抢'
        if typeString == 'FQT':
            item["newsType"] = '其他'
        item["title"] = response.xpath('//*[@class="detatit"]/h4/text()').extract_first()
        item["time"] = '20' + response.xpath('//*[@id="publishdataa"]/text()').extract_first().split('20')[1][0:8]

        text_list = response.xpath('//*[@id="txtContent"]/div/div/div/p')
        if len(text_list) == 0:
            text_list = response.xpath('//*[@id="txtContent"]/div/p/span')
        if len(text_list) == 0:
            text_list = response.xpath('//*[@id="content"]/div/div/p')
        if len(text_list) == 0:
            text_list = response.xpath('//*[@id="txtContent"]/div/p')
        if len(text_list) == 0:
            text_list = response.xpath('//*[@id="artibody"]/p')
        if len(text_list) == 0:
            text_list = response.xpath('//*[@id="txtContent"]/div/div/p')
        if len(text_list) == 0:
            text_list = response.xpath('//*[@id="txtContent"]/p')

        for str_slt in text_list:
            if str_slt.xpath('text()').extract_first() is None:
                self.text = self.text
            else:
                self.text = self.text + str_slt.xpath('text()').extract_first()
        item["text"] = self.text
        self.text = ""

        yield item
