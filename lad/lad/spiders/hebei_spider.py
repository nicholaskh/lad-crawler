#coding=utf-8
import scrapy

from lad.items import LadItem

class newsSpider(scrapy.Spider):
    name = "hebei"
    start_urls = ['http://www.hebga.gov.cn/default.php?mod=article&settype=0&fid=242&s15801039_start=0']
    text = ""
    flag = 0

    def parse(self, response):
        if len(response.xpath('/html/body/center/div/table[3]/tr/td/table/tr/td[3]/table/tr/td/a')) == 23:
            #判断是否是最后一页,不是的话执行下面逻辑
            if len(response.url) == 28:
                next_url = "http://www.cqga.gov.cn/jfzx/default_1.htm"
            else:
                part_str = response.url.split('/')[4]
                num = int(part_str[8])
                next_url_part = "default_" + str(num + 1) + ".htm"
                next_url = "http://www.cqga.gov.cn/jfzx/" + next_url_part
            yield scrapy.Request(url=next_url, callback=self.parse)

        for infoDiv in response.xpath('/html/body/center/div/table[3]/tr/td/table/tr/td[3]/table/tr/td/a'):
            n_url = infoDiv.xpath('@href').extract_first()
            yield scrapy.Request(url=n_url, callback=self.parse_info)

    def parse_info(self, response):
        item = LadItem()

        item["city"] = "重庆"
        item["newsType"] = "警方咨询"
        item["title"] = response.xpath('/html/body/table[4]/tr/td/table[2]/tr/td/text()').extract_first().strip()
        item["time"] = response.xpath('/html/body/table[4]/tr/td/table[4]/tr/td/text()[1]').extract_first().strip()[10:21]

        text_list = response.xpath('//*[@id="Zoom"]/articlepagebegin/div/div/p/span')
        if len(text_list) == 0:
            text_list = response.xpath('//*[@id="Zoom"]/articlepagebegin/div/div/p')
        if len(text_list) == 0:
            text_list = response.xpath('//*[@id="Zoom"]/articlepagebegin/p/span')
        if len(text_list) == 0:
            text_list = response.xpath('//*[@id="Zoom"]/articlepagebegin/p/font/text()')
            self.lag = 1
        if len(text_list) == 0:
            text_list = response.xpath('//*[@id="Zoom"]/articlepagebegin/p')

        if self.flag == 1:
            for str_slt in text_list:
                if str_slt.extract() is None:
                    self.text = self.text
                else:
                    self.text = self.text + str_slt.extract()
            self.flag = 0
        else:
            for str_slt in text_list:
                if str_slt.xpath('text()').extract_first() is None:
                    self.text = self.text
                else:
                    self.text = self.text + str_slt.xpath('text()').extract_first()
        item["text"] = self.text
        self.text = ""

        yield item
