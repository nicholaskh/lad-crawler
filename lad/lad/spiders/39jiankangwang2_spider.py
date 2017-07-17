#coding=utf-8
import scrapy

from lad.items import YangshengItem

class newsSpider(scrapy.Spider):
    name = "39health2"
    whole_list = {}
    dict_commens = {'ys/jkdsy': '1健康大视野','zt/bjrwb': '1精彩热点',
        'ys/shyp': '2生活用品','ys/shcs': '2生活常识','ys/shxg': '2生活习惯','ys/yswq': '2养生误区',
        'ys/jj': '2居家保健','dzbj': '1保健人群','dzbj/woman': '2女性保健','dzbj/man': '2男性保健',
        'dzbj/oldman': '2老人保健','dzbj/baby': '2儿童保健','ys/mxys': '2名人养生','sjbj': '1四季保健',
        'sjbj/cjbj': '2春季保健','sjbj/cjbj': '2夏季保健','sjbj/qjbj': '2秋季保健','sjbj/cjbj': '2冬季保健',
        'jbyf/jzb': '2颈椎病','jbyf/az': '2癌症','jbyf/xxg': '2心血管','yjk/zzyf/sm': '2失眠',
        'yjk/zzyf/pl': '2疲劳','yjk/zzyf/zhz': '2综合症','ys/jkjj': '1健康纠结','ys/jkjj': '1养生指南'
    }

    start_urls = ['http://news.39.net/%s/' % x for x in dict_commens.keys()]
    text = ""

    def parse(self, response):
        if len(response.xpath('/html/body/div/div/div/a')) == 26:
            #判断是否是最后一页,不是的话执行下面逻辑
            if len(response.url) == 28:
                next_url = 'http://www.cndzys.com/zixun/index2.html'
            else:
                num = int(response.url.split('index')[1].split('.')[0])
                next_url = 'http://www.cndzys.com/zixun/index' + str(num + 1) + ".html"
            yield scrapy.Request(url=next_url, callback=self.parse)

        for infoDiv in response.xpath('/html/body/div/div/div/a/@href')[0]:
            n_url = 'http://www.cndzys.com' + infoDiv.extract()
            yield scrapy.Request(url=n_url, callback=self.parse_info)

    def parse_info(self, response):
        item = YangshengItem()

        item["web"] = "大众养生网"
        item["title"] = response.xpath('/html/body/div/div/div/h1/text()').extract_first()
        item["yangsheng_type"] = "养生资讯"
        time_leng = len(response.xpath('/html/body/div/div/div/text()')[18].extract().strip())
        item["time"] = response.xpath('/html/body/div/div/div/div/span/text()')[1].extract()[3:13]

        text_list = response.xpath('/html/body/div/div/div/p/text()')

        for p_slt in text_list:
            if p_slt.extract() is None:
                self.text = self.text
            else:
                self.text = self.text + p_slt.extract()
        item["text"] = self.text
        self.text = ""

        yield item
