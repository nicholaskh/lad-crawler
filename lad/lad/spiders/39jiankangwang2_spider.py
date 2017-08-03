#coding=utf-8
import scrapy

from lad.items import YangshengwangItem

class newsSpider(scrapy.Spider):
    name = "39health2"
    whole_list = {}
    dict_commens = {'ys/jkdsy': '2健康大视野',
        'ys/shyp': '2生活用品','ys/shcs': '2生活常识','ys/shxg': '2生活习惯','ys/yswq': '2养生误区',
        'ys/jj': '2居家保健','dzbj': '1保健人群','dzbj/woman': '2女性保健','dzbj/man': '2男性保健',
        'dzbj/oldman': '2老人保健','dzbj/baby': '2儿童保健','ys/mxys': '2名人养生',
        'jbyf/jzb': '2颈椎病','jbyf/az': '2癌症','jbyf/xxg': '2心血管','yjk/zzyf/sm': '2失眠',
        'yjk/zzyf/pl': '2疲劳','yjk/zzyf/zhz': '2综合症','ys/jkjj': '2健康纠结','ys/jkjj': '2养生指南'
    }

    # start_urls = ['http://care.39.net/ys/jkdsy/']
    start_urls = ['http://care.39.net/%s/' % x for x in dict_commens.keys()]
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
        item["className"] = response.xpath('//*[@class="ClassNav"]')[-2].xpath('text()').extract_first()
        item["specificName"] = response.xpath('//*[@class="ClassNav"]')[-1].xpath('text()').extract_first()
        item["classNum"] = 2
        item["title"] = response.xpath('//*[@id="art_box"]/div[1]/div[1]/h1/text()').extract_first()
        item["source"] = "39健康网"
        item["sourceUrl"] = response.url
        if response.xpath('//*[@id="contentText"]/p/img/@src').extract() is None:
            item["imageUrls"] = ''
        else:
            item["imageUrls"] = response.xpath('//*[@id="contentText"]/p/img/@src').extract()
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
