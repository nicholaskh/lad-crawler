#coding=utf-8
import scrapy

from lad.items import YangshengwangItem

class newsSpider(scrapy.Spider):
    name = "dazhongyangshengwang"
    districts = ['yinshi', 'yinshi', 'zhongyi', 'shenghuoyangsheng', 'yundong','zixun']
    start_urls = ['http://www.cndzys.com/%s/' % x for x in districts]
    text = ""

    def parse(self, response):
        if response.xpath('//*[@class=" paging"]/span')[-2].xpath('a/text()').extract_first().encode('utf-8') == '下一页':
            #判断是否是最后一页,不是的话执行下面逻辑
            next_url = response.url.split('index')[0] + response.xpath('//*[@class=" paging"]/span')[-2].xpath('a/@href').extract_first()
            yield scrapy.Request(url=next_url, callback=self.parse)

        for infoDiv in response.xpath('//*[@class="con_left"]/div/div/h4/a/@href'):
            n_url = 'http://www.cndzys.com' + infoDiv.extract()
            yield scrapy.Request(url=n_url, callback=self.parse_info)

    def parse_info(self, response):
        item = YangshengwangItem()

        item["module"] = "保健常识"
        item["class_name"] = response.xpath('//*[@class="location"]/a/text()')[-2].extract()
        item["class_num"] = len(response.xpath('//*[@class="location"]/a')) - 1
        item["specific_name"] = response.xpath('//*[@class="location"]/a/text()')[-1].extract()
        item["title"] = response.xpath('/html/body/div/div/div/h1/text()').extract_first()
        item["source"] = '大众养生网'
        item["source_url"] = response.url
        item['image_urls'] = response.xpath('//*[@style="text-align:center;"]/a/img/@src').extract() #提取图片链接
        item["time"] = response.xpath('//*[@class="info"]/span/text()')[1].extract()

        text_list = response.xpath('//*[@class="content_text"]/p/text()')

        for p_slt in text_list:
            if p_slt.extract() is None:
                self.text = self.text
            else:
                self.text = self.text + p_slt.extract()
        item["text"] = self.text
        self.text = ""

        if len(response.xpath('//*[@class=" paging"]/a/text()')) > 0:
            if response.xpath('//*[@class=" paging"]/a/text()')[-1].extract().encode('utf-8') == '下一页':
                n_url = 'http://www.cndzys.com/' + response.xpath('//*[@class=" paging"]/a/@href')[-1].extract()
                yield scrapy.Request(url=n_url, callback=self.parse_info)
        yield item
