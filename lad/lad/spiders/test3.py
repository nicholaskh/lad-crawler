#coding=utf-8
import scrapy
from ..items import YangshengwangItem
from beautifulSoup import processText
from basespider import BaseTimeCheckSpider

class ActualPage(BaseTimeCheckSpider):
    text = ""
    name = "shuhuayuyangsheng"
    start_urls = ['http://www.cpoha.com.cn/shuhua/shuhuayuyangsheng/']

    def parse(self, response):
        urls = response.xpath('//*[@class="e2"]/li/a[2]/@href').extract()
        for each in urls:
            url_new = "http://www.cpoha.com.cn" + each
            yield scrapy.Request(url=url_new, callback=self.parse_info)

    def parse_info(self, response):

        title = response.xpath('//*[@class="left w640"]/h1/text()').extract_first()
        time =  response.xpath('//*[@id="pub_date"]/text()').extract_first()
        introduction = response.xpath('//*[@class="intro"]/text()').extract_first()

        #text = response.xpath('//*[@id="content"]/*')
        item = YangshengwangItem()
        text_list = response.xpath('//*[@id="content"]/p/text()')
        if len(text_list) == 0:
            text_list = response.xpath('//*[@id="content"]/text()')
        for p_slt in text_list:
            self.text = self.text + p_slt.extract()
        item["text"] = self.text
        if len(item["text"]) < 20:
            text_list = response.xpath('//*[@id="content"]/*')
            item["text"] = processText(text_list)
            if len(item["text"]) == 0:
                text_list = response.xpath('//*[@id="content"]/span/*')
                item["text"] = processText(text_list)
        self.text = ""

        # item['web'] = "书画与养生"
        item['sourceUrl'] = response.url
        item['time'] = time
        item['title'] = title
        # item['yangshengType'] = introduction
        #item['text'] = processText(text)

        yield item
