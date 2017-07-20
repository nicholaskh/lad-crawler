#coding=utf-8
import scrapy

from lad.items import YangshengwangItem

class newsSpider(scrapy.Spider):
    name = "99yiji"
    # 健康新知
    dict_news = {'zyys': '1_中医养生', 'zyys/jjys': '2_居家养生','zyys/ysyd': '2_养生有道',
        'zyys/nvys': '2_女人养生','zyys/nvys': '2_男人养生','zyys/sjys': '2_四季养生'}
    start_urls = ['http://zyk.99.com.cn/%s/' % x for x in dict_news.keys()]
    text = ''

    def parse(self, response):
        if len(response.xpath('//*[@class="one_list"]/div')) == 15:
            #判断是否是最后一页,不是的话执行下面逻辑
            if 'html' in response.url:
                num = int(response.url.split('_')[2].split('.')[0])
                next_url = response.url.split('_')[0] + '_' + response.url.split('_')[1] + '_' + str(num - 1) + ".html"
            else:
                next_url = 'http://zyk.99.com.cn/zyys/' + response.xpath('//*[@class="list_page"]/span/a/@href').extract_first()
            yield scrapy.Request(url=next_url, callback=self.parse)

        for infoDiv in response.xpath('//*[@class="one_list"]/div/h2/a/@href'):
            n_url = infoDiv.extract()
            yield scrapy.Request(url=n_url, callback=self.parse_info)

    def parse_info(self, response):
        item = YangshengwangItem()

        item["module"] = "保健常识"
        item["class_name"] = '中医养生'
        item["class_num"] = 1
        item["title"] = response.xpath('//*[@class="title"]/h1/text()').extract_first()
        item["source"] = "99健康网"
        item["source_url"] = response.url
        if response.xpath('//*[@align="center"]/a/img/@src').extract() is None:
            item["image_urls"] = ''
        else:
            item["image_urls"] = response.xpath('//*[@align="center"]/a/img/@src').extract()
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
