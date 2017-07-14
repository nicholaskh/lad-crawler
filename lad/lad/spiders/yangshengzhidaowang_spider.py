#coding=utf-8
import scrapy

from lad.items import YangshengItem

class newsSpider(scrapy.Spider):
    name = "yangshengzhidaowang"
    start_urls = ['https://www.ys137.com/xinwen/']
    news_type = ""
    text = ""

    def parse(self, response):
        if response.xpath('/html/body/div/div/ul/li/div/span/text()')[19].extract() != '2014-08-25 15:03':
            #判断是否是最后一页,不是的话执行下面逻辑
            if len(response.url) == 29:
                next_url = 'https://www.ys137.com/xinwen/list_183_1150.html'
            else:
                num = int(response.url.split('_')[2].split('.')[0])
                next_url = 'https://www.ys137.com/xinwen/list_183_' + str(num - 1) + ".html"
            yield scrapy.Request(url=next_url, callback=self.parse)

        for infoDiv in response.xpath('/html/body/div/div/ul/li/div/h2/a/@href'):
            n_url = infoDiv.extract()
            yield scrapy.Request(url=n_url, callback=self.parse_info)

    def parse_info(self, response):
        item = YangshengItem()

        item["web"] = "养生之道网"
        item["title"] = response.xpath('/html/body/div/div/h1/text()').extract_first()
        item["yangsheng_type"] = "养生资讯"
        time_leng = len(response.xpath('/html/body/div/div/div/text()')[18].extract().strip())
        item["time"] = response.xpath('/html/body/div/div/div/text()')[18].extract().strip()[time_leng-16:time_leng]

        text_list = response.xpath('/html/body/div/div/div/table/tr/td/p/text()')

        for p_slt in text_list:
            if p_slt.extract() is None:
                self.text = self.text
            else:
                self.text = self.text + p_slt.extract()
        item["text"] = self.text
        self.text = ""

        yield item
