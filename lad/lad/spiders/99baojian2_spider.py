#coding=utf-8
import scrapy

from lad.items import YangshengwangItem

class newsSpider(scrapy.Spider):
    name = "99yiji2"
    # 健康新知
    dict_news = ['rqbj','sjbj','yajiankang','lybj','baojiancao','jjbj']
    start_urls = ['http://bj.99.com.cn/%s/' % x for x in dict_news]
    text = ''

    def parse(self, response):
        if len(response.xpath('//*[@class="one_list"]/div')) == 15:
            #判断是否是最后一页,不是的话执行下面逻辑
            if 'html' in response.url:
                num = int(response.url.split('-')[1].split('.')[0])
                next_url = response.url.split('-')[0] + '-' + str(num - 1) + ".htm"
            else:
                next_url = response.url + response.xpath('//*[@class="list_page"]/span/a/@href').extract_first()
            yield scrapy.Request(url=next_url, callback=self.parse)

        for infoDiv in response.xpath('//*[@class="one_list"]/div/h2/a/@href'):
            n_url = infoDiv.extract()
            yield scrapy.Request(url=n_url, callback=self.parse_info)

    def parse_info(self, response):
        item = YangshengwangItem()

        item["module"] = "保健常识"
        item["className"] = response.xpath('//*[@class="l_path"]/span/a/text()')[-2].extract()
        item["classNum"] = 2
        item["specificName"] = response.xpath('//*[@class="l_path"]/span/a/text()')[-1].extract()
        item["title"] = response.xpath('//*[@class="title"]/h1/text()').extract_first()
        item["source"] = "99健康网"
        item["sourceUrl"] = response.url
        if response.xpath('//*[@align="center"]/a/img/@src').extract() is None:
            item["imageUrls"] = ''
        else:
            item["imageUrls"] = response.xpath('//*[@align="center"]/a/img/@src').extract()
        item["time"] = response.xpath('//*[@class="l_time"]/span/text()').extract_first()

        text_list = response.xpath('//*[@id="Page"]/div/div/div/div/div/p/text()')

        for p_slt in text_list:
            if p_slt.extract() is None:
                self.text = self.text
            else:
                self.text = self.text + p_slt.extract()
        item["text"] = self.text
        self.text = ""

        yield item
