#coding=utf-8
import scrapy

from lad.items import LadItem

class newsSpider(scrapy.Spider):
    name = "shandong"
    start_urls = ['http://www.sdga.gov.cn/col/col23/index.html']
    text = ""

    def parse(self, response):
        if len(response.xpath('/html/body/div/table[1]/tr/td[3]/table[5]/tr/td/table/tr/td/table/tr[2]/td/table/tr/td/div/a')) == 20:
            #判断是否是最后一页,不是的话执行下面逻辑
            if len(response.url) == 45:
                next_url = 'http://www.njga.gov.cn/www/njga/2010/zabb_p1.htm'
            else:
                num = int(response.url.split('/')[6][6])
                next_url = 'http://www.njga.gov.cn/www/njga/2010/zabb_p' + str(num + 1) + ".htm"
            yield scrapy.Request(url=next_url, callback=self.parse)

        for infoDiv in response.xpath('/html/body/div/table[1]/tr/td[3]/table[5]/tr/td/table/tr/td/table/tr[2]/td/table/tr/td/div/a/@href'):
            n_url = "http://www.njga.gov.cn/www/njga/2010/" + infoDiv.extract()
            yield scrapy.Request(url=n_url, callback=self.parse_info)

    def parse_info(self, response):
        item = LadItem()

        item["city"] = "南京"
        item["newsType"] = "治安播报"
        item["title"] = response.xpath('/html/body/div/table[1]/tr/td[3]/table[5]/tr/td/table/tr/td/table/tr[2]/td/center/table[2]/tr[1]/td/div/strong/text()').extract_first().strip()
        time_leng = len(response.xpath('/html/body/div/table[1]/tr/td[3]/table[5]/tr/td/table/tr/td/table/tr[2]/td/center/table[2]/tr[2]/td/div/text()[1]').extract_first().strip().split(']')[0].strip())
        item["time"] = response.xpath('/html/body/div/table[1]/tr/td[3]/table[5]/tr/td/table/tr/td/table/tr[2]/td/center/table[2]/tr[2]/td/div/text()[1]').extract_first().strip().split(']')[0].strip()[time_leng - 10 : time_leng]
        text_list = response.xpath('/html/body/div/table[1]/tr/td[3]/table[5]/tr/td/table/tr/td/table/tr[2]/td/center/table[3]/tr/td/div/div/div/span/text()')

        for p_slt in text_list:
            if p_slt.extract() is None:
                self.text = self.text
            else:
                self.text = self.text + p_slt.extract()
        item["text"] = self.text
        self.text = ""

        yield item
