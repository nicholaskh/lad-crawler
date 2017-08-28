#coding=utf-8
import scrapy

from lad.items import LadItem

class newsSpider(scrapy.Spider):
    name = "lasa"
    districts = ['jingwuxinwen', 'yinshijingxun']
    start_urls = ['http://ga.lasa.gov.cn/%s/' % x for x in districts]
    text = ""

    def parse(self, response):
        if len(response.xpath('/html/body/section/section/div/div[2]/ul/li')) == 20:
            #判断是否是最后一页,不是的话执行下面逻辑
            if len(response.url) <= 36:
                next_url = response.url[0:len(response.url) - 1] + "?pageIndex=2"
            else:
                num = int(response.url.split('=')[1]) + 1
                next_url = response.url.split('pageIndex')[0] + "pageIndex=" + '%s' %num
            yield scrapy.Request(url=next_url, callback=self.parse)

        for infoDiv in response.xpath('/html/body/section/section/div/div[2]/ul/li'):
            info_url = infoDiv.xpath('div/h4/a/@href').extract_first()
            n_url = "http://ga.lasa.gov.cn" + info_url
            yield scrapy.Request(url=n_url, callback=self.parse_info)

    def parse_info(self, response):
        item = LadItem()

        item["city"] = "拉萨"
        item['newsType'] = '警事要闻'
        item["title"] = response.xpath('/html/body/section/section/div/h2/text()').extract_first()
        c = response.xpath('/html/body/section/section/div/h6/b[3]/span/text()').extract_first().split(' ')[0].split('/')
        item["time"] = c[0] + '-' + c[1] + '-' + c[2]

        text_list = response.xpath('/html/body/section/section/div/section/p')
        if len(text_list) == 0:
            text_list = response.xpath('//*[@class="main_para_txt"]/p')

        for str_slt in text_list:
            if str_slt.xpath('text()').extract_first() is None:
                self.text = self.text
            else:
                self.text = self.text + str_slt.xpath('text()').extract_first()
        item["text"] = self.text
        self.text = ""

        yield item
