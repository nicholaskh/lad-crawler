#coding=utf-8
import scrapy

from lad.items import LadItem

class newsSpider(scrapy.Spider):
    name = "guangzhou"
    start_urls = ['http://www.gzjd.gov.cn/gzjdw/gaxw/ztbd/ffzp/index.shtml']
    text = ""
    flag = 0

    def parse(self, response):
        if response.xpath('/html/body/div[2]/section/div/div[2]/div[2]/ul/li/table/tr/td/span/text()')[9].extract()[0:9] != '2001-7-12':
            #判断是否是最后一页,不是的话执行下面逻辑
            if len(response.url) == 55:
                next_url = "http://www.gzjd.gov.cn/gzjdw/gaxw/ztbd/ffzp/list-2.shtml"
            else:
                part_str = response.url.split('/')[7]
                num = int(part_str[5])
                next_url_part = "list-" + str(num + 1) + ".shtml"
                next_url = "http://www.gzjd.gov.cn/gzjdw/gaxw/ztbd/ffzp/" + next_url_part
            yield scrapy.Request(url=next_url, callback=self.parse)

        for infoDiv in response.xpath('/html/body/div[2]/section/div/div[2]/div[2]/ul/li/table/tr[1]/td/dl/dt/a'):
            n_url = infoDiv.xpath('text()').extract_first()
            yield scrapy.Request(url=n_url, callback=self.parse_info)

    def parse_info(self, response):
        item = LadItem()

        item["city"] = "广州"
        item["news_type"] = "公安新闻"
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
