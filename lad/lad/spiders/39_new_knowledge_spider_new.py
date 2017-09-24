#coding=utf-8
import scrapy

from ..items import YangshengwangItem
from ..spiders.beautifulSoup import processText
from datetime import datetime
from basespider import BaseTimeCheckSpider

class NewsSpider(BaseTimeCheckSpider):

    name = "39newnew"
    start_urls = ['http://news.39.net/xinzhi/']
    text = ""

    def parse(self, response):

        next_url = None
        if len(response.xpath('/html/body/div/ul/li/strong/a')) == 10:
            #判断是否是最后一页,不是的话执行下面逻辑
            if len(response.url) == 26:
                next_url = 'http://news.39.net/xinzhi/index_1.html'
            else:
                num = int(response.url.split('_')[1].split('.')[0])
                next_url = 'http://news.39.net/xinzhi/index_' + str(num + 1) + ".html"
            # yield scrapy.Request(url=next_url, callback=self.parse)

        child_urls = response.xpath('/html/body/div/ul/li/strong/a/@href')
        for infoDiv in child_urls[:-1]:
            n_url = infoDiv.extract()
            child_request = scrapy.Request(url=n_url, callback=self.parse_info)
            m_item = YangshengwangItem()
            m_item['is_final_child'] = False
            child_request.meta['item'] = m_item
            yield child_request

        # 特殊处理最后一个，通过request的meta传递信息
        final_child_url = child_urls[-1].extract()
        final_request = scrapy.Request(url=final_child_url, callback=self.parse_info)
        m_item = YangshengwangItem()
        m_item['is_final_child'] = True
        m_item['next_father_url'] = next_url
        final_request.meta['item'] = m_item
        yield final_request

    def parse_info(self, response):
        item = response.meta['item']
        time = response.xpath('//*[@class="sweetening_title"]/span[2]/text()').extract_first()

        try:
            time_now = datetime.strptime(time, '%Y-%m-%d')
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
        item["module"] = "健康资讯"
        item["className"] = "健康新知"
        item["classNum"] = 1
        item["title"] = response.xpath('/html/body/div/div/div/h1/text()').extract_first()
        if item["title"] is None:
            item["title"] = response.xpath('//*[@class="title1"]/h2/text()').extract_first()
        item["source"] = "39健康网"
        item["sourceUrl"] = response.url
        item['imageUrls'] = response.xpath('//*[@id="contentText"]/p/img/@src').extract() #提取图片链接
        if len(item['imageUrls']) == 0:
            item['imageUrls'] = response.xpath('//*[@class="imgcon1"]/img/@src').extract()
        if len(item['imageUrls']) == 0:
            item['imageUrls'] = response.xpath('//*[@id="contentText"]/center/img/@src').extract_first()
        item["time"] = response.xpath('//*[@class="sweetening_title"]/span[2]/text()').extract_first()

        text_list = response.xpath('//*[@id="contentText"]/*')
        if len(text_list) == 0:
            text_list = response.xpath('//*[@class="detail_con"]/*')

        item["text"] = processText(text_list)
        self.text = ""

        yield item

        # 在最后一个孩子哪儿判断是否需要爬取下一页，如果代码没有执行到这儿，那么说明下一页的时间已经是无效的时间了
        if item['is_final_child'] and item['next_father_url'] is not None:
            yield scrapy.Request(url=item['next_father_url'], callback=self.parse)
