#coding=utf-8
import scrapy

from lad.items import YangshengwangItem
from lad.spiders.beautifulSoup import processText

class newsSpider(scrapy.Spider):
    name = "99yiji"
    # 健康新知
    dict_news = {'zyys/jjys': '2_居家养生','zyys/ysyd': '2_养生有道',
        'zyys/nvys': '2_女人养生','zyys/nvys': '2_男人养生','zyys/sjys': '2_四季养生','zyjb': '中医疾病','changshi': '中医常识'}
    start_urls = ['http://zyk.99.com.cn/%s/' % x for x in dict_news.keys()]

    def parse(self, response):
        if len(response.xpath('//*[@class="one_list"]/div')) == 15:
            #判断是否是最后一页,不是的话执行下面逻辑
            if 'html' in response.url:
                num = int(response.url.split('_')[2].split('.')[0])
                next_url = response.url.split('_')[0] + '_' + response.url.split('_')[1] + '_' + str(num - 1) + ".html"
            else:
                next_url = 'http://zyk.99.com.cn/zyys/jjys/' + response.xpath('//*[@class="list_page"]/span/a/@href').extract_first()
            yield scrapy.Request(url=next_url, callback=self.parse)

        for infoDiv in response.xpath('//*[@class="one_list"]/div/h2/a/@href'):
            n_url = infoDiv.extract()
            yield scrapy.Request(url=n_url, callback=self.parse_info)

    def parse_info(self, response):
        item = YangshengwangItem()

        item["module"] = "保健常识"
        item["className"] = response.xpath('//*[@class="l_path"]/span/a/text()')[-2].extract()
        item["classNum"] = 2
        item['specificName'] = response.xpath('//*[@class="l_path"]/span/a/text()')[-1].extract()
        item["title"] = response.xpath('//*[@class="title"]/h1/text()').extract_first()
        item["source"] = "99健康网"
        item["sourceUrl"] = response.url
        if response.xpath('//*[@align="center"]/a/img/@src').extract() is None:
            item["imageUrls"] = ''
        else:
            item["imageUrls"] = response.xpath('//*[@align="center"]/a/img/@src').extract()
        item["time"] = response.xpath('//*[@class="l_time"]/span/text()').extract_first().split(' ')[0]

        text_list = response.xpath('//*[@id="Page"]/div/div/div/div/div/*')

        item["text"] = processText(text_list)

        yield item
