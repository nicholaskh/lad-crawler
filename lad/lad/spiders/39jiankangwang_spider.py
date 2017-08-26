#coding=utf-8
import scrapy

from lad.items import YangshengwangItem
from lad.spiders.beautifulSoup import processText

class newsSpider(scrapy.Spider):
    name = "39health1"
    whole_list = {}
    dict_news = {'jbyw': '1疾病要闻', 'ysbj/ys': '1食品安全','mxrd': '1健康星闻',
        'qwqs': '1健康奇闻','interview': '1医药名人堂','yltx': '1医院动态','shwx': '1社会万象',
        'kyfx': '1科研发现','hxw': '1曝光台','jdxw': '1焦点资讯'}
    start_urls = ['http://news.39.net/%s/' % x for x in dict_news.keys()]
    text = ""

    def parse(self, response):
        if response.xpath('//*[@class="list_page"]/span/a/text()')[-2].extract().encode('utf-8') == '下一页':
            #判断是否是最后一页,不是的话执行下面逻辑
            if len(response.url) <= 29:
                next_url = response.url + 'index_1.html'
            else:
                num = int(response.url.split('_')[1][0])
                next_url = response.url.split('_')[0] + '_' + str(num + 1) + ".html"
            yield scrapy.Request(url=next_url, callback=self.parse)

        for infoDiv in response.xpath('//*[@class="listbox"]/ul/li/span/a/@href'):
            n_url = infoDiv.extract()
            yield scrapy.Request(url=n_url, callback=self.parse_info)

    def parse_info(self, response):
        item = YangshengwangItem()

        item["module"] = "健康资讯"
        key_name = response.url.split('/')[3]
        len_str = len(self.dict_news[key_name])
        item["className"] = self.dict_news[key_name][1:len_str]
        item["classNum"] = 1
        item["title"] = response.xpath('//*[@id="art_box"]/div[1]/div[1]/h1/text()').extract_first()
        item["source"] = "39健康网"
        item["sourceUrl"] = response.url
        item["imageUrls"] = ''
        item["time"] = response.xpath('//*[@id="art_box"]/div[1]/div[1]/div[1]/div[2]/em[1]/text()').extract_first()

        text_list = response.xpath('//*[@id="contentText"]/*')
        if len(text_list) == 0:
            text_list = response.xpath('//*[@class="article"]/*')

        item["text"] = processText(text_list)
        self.text = ""

        yield item
