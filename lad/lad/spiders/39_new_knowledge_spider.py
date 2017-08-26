#coding=utf-8
import scrapy

from lad.items import YangshengwangItem
from lad.spiders.beautifulSoup import processText

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
                num = int(response.url.split('_')[1].split('.')[0])
                next_url = 'http://news.39.net/xinzhi/index_' + str(num + 1) + ".html"
            yield scrapy.Request(url=next_url, callback=self.parse)

        for infoDiv in response.xpath('/html/body/div/ul/li/strong/a/@href'):
            n_url = infoDiv.extract()
            yield scrapy.Request(url=n_url, callback=self.parse_info)

    def parse_info(self, response):
        item = YangshengwangItem()

        item["module"] = "健康资讯"
        item["className"] = "健康新知"
        item["classNum"] = 1
        item["title"] = response.xpath('/html/body/div/div/div/h1/text()').extract_first()
        if item["title"] is None:
            item["title"] = response.xpath('//*[@class="title1"]/h2/text()').extract_first()
        item["source"] = "39健康网"
        item["sourceUrl"] = response.url
        item['imageUrls'] = response.xpath('//*[@id="contentText"]/p/img/@src').extract() #提取图片链接
        if len(item['imageUrls']) == 0:
            item['imageUrls'] = response.xpath('//*[@class="imgcon1"]/img/@src').extract()
        if len(item['imageUrls']) == 0:
            item['imageUrls'] = response.xpath('//*[@id="contentText"]/center/img/@src').extract_first()
        item["time"] = response.xpath('//*[@class="sweetening_title"]/span[2]/text()').extract_first()

        text_list = response.xpath('//*[@id="contentText"]/*')
        if len(text_list) == 0:
            text_list = response.xpath('//*[@class="detail_con"]/*')

        item["text"] = processText(text_list)
        self.text = ""

        yield item
