#coding=utf-8
import scrapy

from ..items import LadItem
from ..spiders.beautifulSoup import processText
from datetime import datetime
from basespider import BaseTimeCheckSpider

class NewsSpider(BaseTimeCheckSpider):

    name = "lanzhounew"
    districts = ['jcjx', 'mt', 'xwfb']
    start_urls = ['http://www.lzsgaj.gov.cn/gaxw/%s/index.shtml' % x for x in districts]

    def parse(self, response):

        next_url = None
        if len(response.xpath('//*[@id="mid"]/ul/li')) == 20:
            if len(response.url) == 46 or len(response.url) == 44:
                next_url = response.url.split('index')[0] + "index_2.shtml"
            else:
                part_str = response.url.split('/')[5]
                num = int(part_str[6])
                next_url_part = "index_" + str(num + 1) + ".shtml"
                next_url = response.url.split('index')[0] + next_url_part

        child_urls = response.xpath('//*[@id="mid"]/ul/li/a/@href')
        for infoDiv in child_urls[:-1]:
            n_url = 'http://www.lzsgaj.gov.cn' + infoDiv.extract().split('..')[2]
            child_request = scrapy.Request(url=n_url, callback=self.parse_info)
            m_item = LadItem()
            m_item['is_final_child'] = False
            child_request.meta['item'] = m_item
            yield child_request

        # 特殊处理最后一个，通过request的meta传递信息
        final_child_url = 'http://www.lzsgaj.gov.cn' + child_urls[-1].extract().split('..')[2]
        final_request = scrapy.Request(url=final_child_url, callback=self.parse_info)
        m_item = LadItem()
        m_item['is_final_child'] = True
        m_item['next_father_url'] = next_url
        final_request.meta['item'] = m_item
        yield final_request

    def parse_info(self, response):
        item = response.meta['item']
        time = response.xpath('//*[@id="mid"]/div[2]/div[1]/text()[1]').extract_first().strip()[5:21]

        try:
            time_now = datetime.strptime(time, '%Y-%m-%d %H:%M')
            print(time_now)
            # 更新将要保存到MONGODB中的时间
            self.update_last_time(time_now)
        except:
            print("Something wrong")
            return

        if self.last_time is not None and self.last_time >= time_now:
            print(u'spider: %s 这篇文章已经存在' % self.url)
            return
        item["city"] = "兰州"
        item["newsType"] = '警事要闻'
        item["title"] = response.xpath('//*[@id="mid"]/div[2]/h1/font/text()').extract_first()
        item["time"] = response.xpath('//*[@id="mid"]/div[2]/div[1]/text()[1]').extract_first().strip()[5:15]

        text_list = response.xpath('//*[@id="content"]/*')
        item["text"] = processText(text_list)

        yield item

        # 在最后一个孩子哪儿判断是否需要爬取下一页，如果代码没有执行到这儿，那么说明下一页的时间已经是无效的时间了
        if item['is_final_child'] and item['next_father_url'] is not None:
            yield scrapy.Request(url=item['next_father_url'], callback=self.parse)
