#coding=utf-8
import scrapy

from lad.items import YangshengwangItem

class newsSpider(scrapy.Spider):
    # 四季养生
    name = "dazhongyangshengwang2"
    districts = ['3.html', '47.html', '48.html', '49.html']
    start_urls = ['http://www.cndzys.com/jijie/siji/%s' % x for x in districts]
    text = ""

    def parse(self, response):
        item = YangshengwangItem()

        item["module"] = "保健常识"
        item["className"] = '四季保健'
        item["classNum"] = 3
        item["specificName"] = response.xpath('//*[@class="con_left"]/h1/text()').extract_first()
        item["title"] = response.xpath('//*[@class="con_left"]/h1/text()').extract_first()
        item["source"] = '大众养生网'
        item["sourceUrl"] = response.url
        item['imageUrls'] = response.xpath('//*[@style="text-align:center;"]/a/img/@src').extract() #提取图片链接
        item["time"] = response.xpath('//*[@class="info"]/span/text()')[1].extract()

        text_list = response.xpath('//*[@class="main"]/p/text()')

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
