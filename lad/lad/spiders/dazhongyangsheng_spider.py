#coding=utf-8
import scrapy

from lad.items import YangshengItem

class newsSpider(scrapy.Spider):
    name = "dazhongyangshengwang"
    start_urls = ['http://www.cndzys.com/zixun/']
    text = ""

    def parse(self, response):
        if len(response.xpath('/html/body/div/div/div/a')) == 26:
            #判断是否是最后一页,不是的话执行下面逻辑
            if len(response.url) == 28:
                next_url = 'http://www.cndzys.com/zixun/index2.html'
            else:
                num = int(response.url.split('index')[1].split('.')[0])
                next_url = 'http://www.cndzys.com/zixun/index' + str(num + 1) + ".html"
            yield scrapy.Request(url=next_url, callback=self.parse)

        for infoDiv in response.xpath('/html/body/div/div/div/a/@href')[0]:
            n_url = 'http://www.cndzys.com' + infoDiv.extract()
            yield scrapy.Request(url=n_url, callback=self.parse_info)

    def parse_info(self, response):
        item = YangshengItem()

        item["web"] = "大众养生网"
        item["title"] = response.xpath('/html/body/div/div/div/h1/text()').extract_first()
        item["yangsheng_type"] = "养生资讯"
        time_leng = len(response.xpath('/html/body/div/div/div/text()')[18].extract().strip())
        item["time"] = response.xpath('/html/body/div/div/div/div/span/text()')[1].extract()[3:13]

        text_list = response.xpath('/html/body/div/div/div/p/text()')

        for p_slt in text_list:
            if p_slt.extract() is None:
                self.text = self.text
            else:
                self.text = self.text + p_slt.extract()
        item["text"] = self.text
        self.text = ""

        yield item
