#coding=utf-8
import scrapy

from lad.items import YangshengwangItem

class newsSpider(scrapy.Spider):
    name = "39new"
    # 健康新知
    start_urls = ['http://news.39.net/xinzhi/']
    text = ""

    def parse(self, response):
        if len(response.xpath('/html/body/div/ul/li/strong/a')) == 10:
            #判断是否是最后一页,不是的话执行下面逻辑
            if len(response.url) == 26:
                next_url = 'http://news.39.net/xinzhi/index_1.html'
            else:
                num = int(response.url.split('_')[1][0])
                next_url = 'http://news.39.net/xinzhi/index_' + str(num + 1) + ".html"
            yield scrapy.Request(url=next_url, callback=self.parse)

        for infoDiv in response.xpath('/html/body/div/ul/li/strong/a/@href'):
            n_url = infoDiv.extract()
            yield scrapy.Request(url=n_url, callback=self.parse_info)

    def parse_info(self, response):
        item = YangshengwangItem()

        item["module"] = "健康资讯"
        item["class_name"] = "健康新知"
        item["class_num"] = 1
        item["title"] = response.xpath('/html/body/div/div/div/h1/text()').extract_first()
        item["source"] = "大众养生网"
        item["source_url"] = response.url
        item['image_urls'] = response.xpath('//*[@id="contentText"]/p/img/@src').extract() #提取图片链接
        item["time"] = response.xpath('//*[@class="sweetening_title"]/span[2]/text()').extract_first()

        text_list = response.xpath('//*[@id="contentText"]/p/text()')

        for p_slt in text_list:
            if p_slt.extract() is None:
                self.text = self.text
            else:
                self.text = self.text + p_slt.extract()
        item["text"] = self.text
        self.text = ""

        yield item
