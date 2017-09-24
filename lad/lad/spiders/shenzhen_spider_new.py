#coding=utf-8
import scrapy

from ..items import LadItem
from ..spiders.beautifulSoup import processText
from datetime import datetime
from basespider import BaseTimeCheckSpider

class NewsSpider(BaseTimeCheckSpider):

    name = "shenzhennew"
    districts = ['FH', 'FD', 'FP', 'FSG', 'FQT', 'FQ']
    start_urls = ['http://www.szga.gov.cn/JFZX/JFTS/%s/' % x for x in districts]

    def parse(self, response):

        next_url = None
        if len(response.xpath('//*[@class="listnums"]/li/a/@href')) == 15:
            #判断是否是最后一页,不是的话执行下面逻辑
            if len(response.url) < 38:
                next_url_part = "index_" + str(1) + ".htm"
                next_url = response.url + next_url_part
            else:
                part_str = response.url.split('/')[6]
                num = int(part_str[6])
                next_url_part = "index_" + str(num + 1) + ".htm"
                url_len = len(response.url)
                next_url = response.url[0:(url_len) - 12] + '/' + next_url_part
            # yield scrapy.Request(url=next_url, callback=self.parse)

        child_urls = response.xpath('//*[@class="listnums"]/li/a/@href')
        for infoDiv in child_urls[:-1]:
            n_url = response.url.split('index')[0] + infoDiv.extract().split('./')[1]
            child_request = scrapy.Request(url=n_url, callback=self.parse_info)
            m_item = LadItem()
            m_item['is_final_child'] = False
            child_request.meta['item'] = m_item
            yield child_request

        # 特殊处理最后一个，通过request的meta传递信息
        final_child_url = response.url.split('index')[0] + child_urls[-1].extract().split('./')[1]
        final_request = scrapy.Request(url=final_child_url, callback=self.parse_info)
        m_item = LadItem()
        m_item['is_final_child'] = True
        m_item['next_father_url'] = next_url
        final_request.meta['item'] = m_item
        yield final_request

    def parse_info(self, response):
        item = response.meta['item']
        time = '20' + response.xpath('//*[@id="publishdataa"]/text()').extract_first().split('20')[1][0:14]

        try:
            time_now = datetime.strptime(time, '%Y-%m-%d %H:%M')
            # 更新将要保存到MONGODB中的时间
            self.update_last_time(time_now)
        except:
            return

        if self.last_time is not None and self.last_time >= time_now:
            print(u'spider: %s 这篇文章已经存在' % self.url)
            return
        # next_requests = list()
        #if should_deep:
        # 表示有新的url
        item["city"] = "深圳"
        typeString = response.url.split('/')[5]
        if typeString == 'FH':
            item["newsType"] = '防火'
        if typeString == 'FD':
            item["newsType"] = '防盗'
        if typeString =='FP':
            item["newsType"] = '防骗'
        if typeString == 'FSG':
            item["newsType"] = '防事故'
        if typeString == 'FQ':
            item["newsType"] = '防抢'
        if typeString == 'FQT':
            item["newsType"] = '其他'
        item["title"] = response.xpath('//*[@class="detatit"]/h4/text()').extract_first()
        item["time"] = '20' + response.xpath('//*[@id="publishdataa"]/text()').extract_first().split('20')[1][0:8]
        item["sourceUrl"] = response.url

        text_list = response.xpath('//*[@id="txtContent"]/*')
        item["text"] = processText(text_list)

        yield item

        # 在最后一个孩子哪儿判断是否需要爬取下一页，如果代码没有执行到这儿，那么说明下一页的时间已经是无效的时间了
        if item['is_final_child'] and item['next_father_url'] is not None:
            yield scrapy.Request(url=item['next_father_url'], callback=self.parse)
