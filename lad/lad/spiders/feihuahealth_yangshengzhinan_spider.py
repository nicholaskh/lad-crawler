#coding=utf-8
import scrapy

from lad.items import YangshengwangItem

class newsSpider(scrapy.Spider):
    name = "feihua1"
    # 健康新知
    start_urls = ['http://care.fh21.com.cn/yszn/']
    text = ""

    def parse(self, response):
        if len(response.xpath('//*[@class="ls-mod"]/div/a')) == 13:
            #判断是否是最后一页,不是的话执行下面逻辑
            if len(response.url) == 29:
                next_url = 'http://care.fh21.com.cn/yszn/list_6529_2.html'
            else:
                num = int(response.url.split('_')[2][0])
                next_url = 'http://care.fh21.com.cn/yszn/list_6529_' + str(num + 1) + ".html"
            yield scrapy.Request(url=next_url, callback=self.parse)

        for infoDiv in response.xpath('//*[@class="ls-mod"]/div/a/@href'):
            n_url = 'http://care.fh21.com.cn' + infoDiv.extract()
            yield scrapy.Request(url=n_url, callback=self.parse_info)

    def parse_info(self, response):
        item = YangshengwangItem()

        item["module"] = "保健常识"
        item["className"] = "养生指南"
        item["classNum"] = 1
        item["title"] = response.xpath('//*[@class="arti-head"]/h2/text()').extract_first()
        item["source"] = "飞华保健网"
        item["sourceUrl"] = response.url
        if response.xpath('//*[@style="text-align: center;"]/img/@src').extract() is None:
            item["imageUrls"] = ''
        else:
            item["imageUrls"] = response.xpath('//*[@style="text-align: center;"]/img/@src').extract()
        item["time"] = response.xpath('/html/body/div[4]/div/div[1]/div[2]/div[1]/div/span/text()').extract_first().strip()

        text_list = response.xpath('//*[@class="arti-content"]/p/text()')

        for p_slt in text_list:
            if p_slt.extract() is None:
                self.text = self.text
            else:
                self.text = self.text + p_slt.extract()
        item["text"] = self.text
        self.text = ""

        yield item
