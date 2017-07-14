#coding=utf-8
import scrapy

from lad.items import LadItem

class newsSpider(scrapy.Spider):
    name = "liaoning"
    start_urls = ['http://www.lnga.gov.cn/jwzx/jfts/']
    text = ""

    def parse(self, response):
        if len(response.xpath('//*[@id="left"]/div[2]/li/a/@href')) == 24:
            #判断是否是最后一页,不是的话执行下面逻辑
            if len(response.url) == 33:
                next_url = 'http://www.lnga.gov.cn/jwzx/jfts/index_1.html'
            else:
                num = int(response.url.split('_')[1][0])
                next_url = 'http://www.lnga.gov.cn/jwzx/jfts/index_' + str(num + 1) + ".html"
            yield scrapy.Request(url=next_url, callback=self.parse)

        for infoDiv in response.xpath('//*[@id="left"]/div[2]/li/a/@href'):
            n_url_part_sec = infoDiv.extract()
            n_url_part_leng = len(n_url_part_sec)
            n_url_part = n_url_part_sec[1:n_url_part_leng]
            n_url = "http://www.lnga.gov.cn/jwzx/jfts" + n_url_part
            yield scrapy.Request(url=n_url, callback=self.parse_info)

    def parse_info(self, response):
        item = LadItem()

        item["city"] = "辽宁"
        item["news_type"] = "警方提示"
        item["title"] = response.xpath('//*[@id="activity-name"]/text()').extract_first().strip()
        item["time"] = response.xpath('//*[@id="post-date"]/text()').extract_first()

        text_list = response.xpath('//*[@id="js_content"]/p/span/text()')

        for p_slt in text_list:
            if p_slt.extract() is None:
                self.text = self.text
            else:
                self.text = self.text + p_slt.extract()
        item["text"] = self.text
        self.text = ""

        yield item
