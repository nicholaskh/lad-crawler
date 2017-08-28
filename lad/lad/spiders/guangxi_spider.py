#coding=utf-8
import scrapy

from lad.items import LadItem
from lad.spiders.beautifulSoup import processText

class newsSpider(scrapy.Spider):
    name = "guangxi"
    districts = ['report', 'alert']
    start_urls = ['http://www.gazx.gov.cn/gxgat/%s/index.jhtml' % x for x in districts]
    text = ""

    def parse(self, response):
        if len(response.xpath('/html/body/div[3]/div[2]/div[2]/div/div[1]/div')) == 20:
            #判断是否是最后一页,不是的话执行下面逻辑
            if len(response.url) <= 47:
                next_url = response.url.split('index')[0] + 'index_2.jhtml'
            else:
                num_part = response.url.split('/')[5]
                num = int(num_part[6])
                next_url_part = "index_" + str(num + 1) + ".jhtml"
                next_url = response.url.split('index')[0] + next_url_part
            yield scrapy.Request(url=next_url, callback=self.parse)

        for infoDiv in response.xpath('/html/body/div[3]/div[2]/div[2]/div/div[1]/div/div[1]/a[2]'):
            info_url = infoDiv.xpath('@href').extract_first()
            n_url = "http://www.gazx.gov.cn" + info_url
            yield scrapy.Request(url=n_url, callback=self.parse_info)

    def parse_info(self, response):
        item = LadItem()

        item["city"] = "广西"
        item["newsType"] = "警事要闻"
        item["title"] = response.xpath('/html/body/div[3]/div[2]/div[2]/div[1]/text()').extract_first()
        item["time"] = response.xpath('//*[@class="dateDetail heightLine"]/text()').extract_first().strip()[0:10]
        #item["time"] = response.xpath('/html/body/div[3]/div[2]/div[2]/div[2]/text()[1]').extract_first().strip()[0:10]

        text_list = response.xpath('//*[@class="text"]/*')
        item["text"] = processText(text_list)
        
        self.text = ""

        yield item
