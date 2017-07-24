#coding=utf-8
import scrapy

from lad.items import YangshengwangItem

class newsSpider(scrapy.Spider):
    name = "39health3"
    whole_list = {}
    dict_commens = {'cjbj/yfjb', 'cjbj/ysmf', 'cjbj/stwl', 'cjbj/qjbj', 'xjbj/xrys',
        'xjbj/jblx', 'xjbj/fsmf', 'xjbj/jkts', 'qjbj/qjys', 'qjbj/qgqz', 'qjbj/qfqb',
        'qjbj/qjhf', 'djbj/fblx', 'djbj/ysyd', 'djbj/sthl', 'djbj/dljb'
    }

    # start_urls = ['http://care.39.net/ys/jkdsy/']
    start_urls = ['http://care.39.net/sjbj/%s/' % x for x in dict_commens]
    text = ""

    def parse(self, response):
        if response.xpath('//*[@class="list_page"]/span/a/text()')[-2].extract().encode('utf-8') == '下一页':
            #判断是否是最后一页,不是的话执行下面逻辑
            if 'html' in response.url:
                num = int(response.url.split('_')[1][0])
                next_url = response.url.split('_')[0] + '_' + str(num + 1) + ".html"
            else:
                next_url = response.url + 'index_1.html'
            yield scrapy.Request(url=next_url, callback=self.parse)

        for infoDiv in response.xpath('//*[@class="listbox"]/ul/li/span/a/@href'):
            n_url = infoDiv.extract()
            yield scrapy.Request(url=n_url, callback=self.parse_info)

    def parse_info(self, response):
        item = YangshengwangItem()

        item["module"] = "保健常识"
        item["class_name"] = response.xpath('//*[@class="ClassNav"]')[-2].xpath('text()').extract_first()
        item["specific_name"] = response.xpath('//*[@class="ClassNav"]')[-1].xpath('text()').extract_first()
        item["class_num"] = 3
        item["title"] = response.xpath('//*[@id="art_box"]/div[1]/div[1]/h1/text()').extract_first()
        item["source"] = "39健康网"
        item["source_url"] = response.url
        if response.xpath('//*[@id="contentText"]/p/img/@src').extract() is None:
            item["image_urls"] = ''
        else:
            item["image_urls"] = response.xpath('//*[@id="contentText"]/p/img/@src').extract()
        item["time"] = response.xpath('//*[@id="art_box"]/div[1]/div[1]/div[1]/div[2]/em[1]/text()').extract_first()

        text_list = response.xpath('//*[@id="contentText"]/p/text()')
        if len(text_list) == 0:
            text_list = response.xpath('//*[@class="article"]/p/text()')

        for p_slt in text_list:
            if p_slt.extract() is None:
                self.text = self.text
            else:
                self.text = self.text + p_slt.extract()
        item["text"] = self.text
        self.text = ""

        yield item
