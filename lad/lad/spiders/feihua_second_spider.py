#coding=utf-8
import scrapy

from lad.items import YangshengwangItem

class newsSpider(scrapy.Spider):
    name = "feihua2"
    # 健康新知
    dict_news = {'cjbj': '6534_春季保健', 'xjbj': '6535_夏季保健','qjbj': '6539_秋季保健',
        'djbj': '6536_冬季保健','nvx': '6531_女性保健','bgs': '6537_白领保健','nxbj': '6530_男性保健',
        'lrbj': '6532_老人保健','ert': '6533_儿童保健'}
    start_urls = ['http://care.fh21.com.cn/%s/' % x for x in dict_news.keys()]
    text = ""

    def parse(self, response):
        if len(response.xpath('//*[@class="ls-mod"]/div')) == 13:
            #判断是否是最后一页,不是的话执行下面逻辑
            if 'html' in response.url:
                num = int(response.url.split('_')[2][0])
                next_url = response.url.split('_')[0] + '_' + response.url.split('_')[1] + '_' + str(num + 1) + ".html"
            else:
                key_value = response.url.split('/')[3]
                num = dict_news[key_value].split('_')[0]
                next_url = response.url + 'list_' + str(num) + '_2.html'
            yield scrapy.Request(url=next_url, callback=self.parse)

        for infoDiv in response.xpath('//*[@class="ls-mod"]/div/div/a/@href'):
            n_url = 'http://care.fh21.com.cn' + infoDiv.extract()
            yield scrapy.Request(url=n_url, callback=self.parse_info)

    def parse_info(self, response):
        item = YangshengwangItem()

        item["module"] = "保健常识"
        item["className"] = "养生指南"
        item["classNum"] = 2
        item["specificName"] = self.dict_news[response.url.split('/')[3]].split('_')[1]
        item["title"] = response.xpath('//*[@class="arti-head"]/h2/text()').extract_first()
        item["source"] = "飞华保健网"
        item["sourceUrl"] = response.url
        if response.xpath('//*[@class="arti-content"]/p/img/@src').extract() is None:
            item["imageUrls"] = ''
        else:
            item["imageUrls"] = response.xpath('//*[@class="arti-content"]/p/img/@src').extract()
        item["time"] = response.xpath('/html/body/div[4]/div/div[1]/div[2]/div[1]/div/span/text()').extract_first().strip().split(' ')[1]

        text_list = response.xpath('//*[@class="arti-content"]/p/text()')

        for p_slt in text_list:
            if p_slt.extract() is None:
                self.text = self.text
            else:
                self.text = self.text + p_slt.extract()
        item["text"] = self.text
        self.text = ""

        yield item
