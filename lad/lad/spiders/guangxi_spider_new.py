#coding=utf-8
import scrapy

from ..items import LadItem
from ..spiders.beautifulSoup import processText
from datetime import datetime
from basespider import BaseTimeCheckSpider

class NewsSpider(BaseTimeCheckSpider):

    name = "guangxinew"
    districts = ['report', 'alert']
    start_urls = ['http://www.gazx.gov.cn/gxgat/%s/index.jhtml' % x for x in districts]

    def parse(self, response):

        next_url = None
        if len(response.xpath('/html/body/div[3]/div[2]/div[2]/div/div[1]/div')) == 20:
            #判断是否是最后一页,不是的话执行下面逻辑
            if len(response.url) <= 47:
                next_url = response.url.split('index')[0] + 'index_2.jhtml'
            else:
                num_part = response.url.split('/')[5]
                num = int(num_part[6])
                next_url_part = "index_" + str(num + 1) + ".jhtml"
                next_url = response.url.split('index')[0] + next_url_part

        child_urls = response.xpath('/html/body/div[3]/div[2]/div[2]/div/div[1]/div/div[1]/a[2]/@href').extract()
        for infoDiv in child_urls[:-1]:
            n_url = "http://www.gazx.gov.cn" + infoDiv
            child_request = scrapy.Request(url=n_url, callback=self.parse_info)
            m_item = LadItem()
            m_item['is_final_child'] = False
            child_request.meta['item'] = m_item
            yield child_request

        # 特殊处理最后一个，通过request的meta传递信息
        final_child_url = child_urls[-1]
        n_url = "http://www.gazx.gov.cn" + final_child_url
        final_request = scrapy.Request(url=n_url, callback=self.parse_info)
        m_item = LadItem()
        m_item['is_final_child'] = True
        m_item['next_father_url'] = next_url
        final_request.meta['item'] = m_item

        yield final_request

    def parse_info(self, response):
        item = response.meta['item']
        time = response.xpath('//*[@class="dateDetail heightLine"]/text()').extract_first().strip()[0:16]

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
        item["sourceUrl"] =response.url
        item["city"] = "广西公安网"
        item["newsType"] = "警事要闻"
        item["title"] = response.xpath('/html/body/div[3]/div[2]/div[2]/div[1]/text()').extract_first()
        item["time"] = response.xpath('//*[@class="dateDetail heightLine"]/text()').extract_first().strip()[0:10]
        #item["time"] = response.xpath('/html/body/div[3]/div[2]/div[2]/div[2]/text()[1]').extract_first().strip()[0:10]

        text_list = response.xpath('//*[@class="text"]/*')
        item["text"] = processText(text_list)

        yield item

        # 在最后一个孩子哪儿判断是否需要爬取下一页，如果代码没有执行到这儿，那么说明下一页的时间已经是无效的时间了
        if item['is_final_child'] and item['next_father_url'] is not None:
            yield scrapy.Request(url=item['next_father_url'], callback=self.parse)
