#coding=utf-8
import scrapy
import re

from lad.items import YangshengwangItem
from lad.spiders.beautifulSoup import processText

class newsSpider(scrapy.Spider):
    # 四季养生
    name = "dazhongyangshengwang2"
    dict_news = {'3.html': '春季保健', '47.html':'夏季保健', '48.html':'秋季保健', '49.html':'冬季保健'}
    start_urls = ['http://www.cndzys.com/jijie/siji/%s' % x for x in dict_news.keys()]
    text = ""

    def parse(self, response):
        item = YangshengwangItem()

        item["module"] = "健康资讯"
        item["className"] = '四季保健'
        item["classNum"] = 2
        key_word = re.search('siji/(.+)', response.url).group(1)
        total_str = self.dict_news[key_word]
        item["specificName"] = total_str
        item["title"] = response.xpath('//*[@class="con_left"]/h1/text()').extract_first()
        item["source"] = '大众养生网'
        item["sourceUrl"] = response.url
        item['imageUrls'] = response.xpath('//*[@style="text-align:center;"]/a/img/@src').extract() #提取图片链接
        item["time"] = response.xpath('//*[@class="Information"]/span[2]/text()').extract_first().encode('utf-8')[-19:]

        text_list = response.xpath('//*[@class="main"]/*')

        item["text"] = processText(text_list)

        if len(response.xpath('//*[@class=" paging"]/a/text()')) > 0:
            if response.xpath('//*[@class=" paging"]/a/text()')[-1].extract().encode('utf-8') == '下一页':
                n_url = 'http://www.cndzys.com/' + response.xpath('//*[@class=" paging"]/a/@href')[-1].extract()
                yield scrapy.Request(url=n_url, callback=self.parse_info)
        yield item
