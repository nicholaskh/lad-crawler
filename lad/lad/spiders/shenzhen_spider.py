#coding=utf-8
import scrapy

from lad.items import LadItem

class newsSpider(scrapy.Spider):
    name = "shenzhen"
    districts = ['FH', 'FD', 'FP', 'FSG', 'FQT', 'FQ']
    start_urls = ['http://www.szga.gov.cn/JFZX/JFTS/%s/' % x for x in districts]
    text = ""

    def parse(self, response):
        if len(response.xpath('/html/body/div/div[1]/div[4]/div[2]/ul/li')) == 16:
            #判断是否是最后一页,不是的话执行下面逻辑
            if len(response.url) < 38:
                next_url_part = "index_" + str(1) + ".html"
                next_url = response.url + next_url_part
            else:
                part_str = response.url.split('/')[6]
                num = int(part_str[6])
                next_url_part = "index_" + str(num + 1) + ".html"
                url_len = len(response.url)
                next_url = response.url[0:(url_len) - 12] + next_url_part
            yield scrapy.Request(url=next_url, callback=self.parse)

        for infoDiv in response.xpath('/html/body/div/div[1]/div[4]/div[2]/ul/li')[1:15]:
            info_url = infoDiv.extract().encode('utf-8').split('.')[1]
            n_url = response.url.split('index')[0] + info_url[1:len(info_url)] + ".html"
            yield scrapy.Request(url=n_url, callback=self.parse_info)

    def parse_info(self, response):
        item = LadItem()

        item["news_type"] = response.url.split('/')[5]
        item["title"] = response.xpath('/html/body/div/div[1]/div[4]/div[1]/h4/text()').extract()[0].encode('utf-8')
        item["time"] = response.xpath('/html/body/div/div[1]/div[4]/div[1]/div/p[2]/text()').extract_first().encode('utf-8').split('：')[1]        #rows = list(array)

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
