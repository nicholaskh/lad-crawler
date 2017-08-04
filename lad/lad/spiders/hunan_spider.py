#coding=utf-8
import scrapy

from lad.items import LadItem

class newsSpider(scrapy.Spider):
    name = "hunan"
    districts = ['jjxw/zakb', 'qfqz/gzff', 'qfqz/jfts']
    start_urls = ['http://www.hnga.gov.cn/hnga/%s/index.html' % x for x in districts]
    text = ""

    def parse(self, response):
        if len(response.xpath('//*[@id="mainnews"]/div[4]/ul/li')) == 25:
            #判断是否是最后一页,不是的话执行下面逻辑
            if len(response.url) == 48:
                next_url_part = "index-2.html"
                next_url = response.url.split('index')[0] + next_url_part
            else:
                num = response.url.split('-')[1][0]
                next_url_part = "index-" + str(num + 1) + ".html"
                next_url = response.url.split('index')[0] + next_url_part
            yield scrapy.Request(url=next_url, callback=self.parse)

        for infoDiv in response.xpath('//*[@id="mainnews"]/div[4]/ul/li/a/@href'):
            info_url = infoDiv.extract()
            n_url = "http://www.hnga.gov.cn" + info_url
            yield scrapy.Request(url=n_url, callback=self.parse_info)

    def parse_info(self, response):
        item = LadItem()

        item["city"] = "湖南"
        item["newsType"] = "警事要闻"
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
