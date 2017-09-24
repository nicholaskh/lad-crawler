#coding=utf-8
import scrapy

from ..items import YangshengwangItem
from ..spiders.beautifulSoup import processText
from datetime import datetime
from basespider import BaseTimeCheckSpider

class NewsSpider(BaseTimeCheckSpider):

    name = "dazhongyangshengwangnew"
    districts = ['yinshi', 'yinshi', 'zhongyi', 'shenghuoyangsheng', 'yundong','zixun']
    start_urls = ['http://www.cndzys.com/%s/' % x for x in districts]

    def parse(self, response):

        next_url = None
        if response.xpath('//*[@class=" paging"]/span')[-2].xpath('a/text()').extract_first().encode('utf-8') == '下一页':
            #判断是否是最后一页,不是的话执行下面逻辑
            next_url = response.url.split('index')[0] + response.xpath('//*[@class=" paging"]/span')[-2].xpath('a/@href').extract_first()

        child_urls = response.xpath('//*[@class="con_left"]/div/div/h4/a/@href')
        for infoDiv in child_urls[:-1]:
            n_url = 'http://www.cndzys.com' + infoDiv.extract()
            child_request = scrapy.Request(url=n_url, callback=self.parse_info)
            m_item = YangshengwangItem()
            m_item['is_final_child'] = False
            child_request.meta['item'] = m_item
            yield child_request

        # 特殊处理最后一个，通过request的meta传递信息
        final_child_url = 'http://www.cndzys.com' + child_urls[-1].extract()
        final_request = scrapy.Request(url=final_child_url, callback=self.parse_info)
        m_item = YangshengwangItem()
        m_item['is_final_child'] = True
        m_item['next_father_url'] = next_url
        final_request.meta['item'] = m_item
        yield final_request

    def parse_info(self, response):
        item = response.meta['item']
        time = response.xpath('//*[@class="info"]/span/text()')[1].extract().encode("utf-8").split('时间:')[1]

        try:
            time_now = datetime.strptime(time, '%Y-%m-%d %H:%M:%S')
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
        item["module"] = "保健常识"
        item["className"] = response.xpath('//*[@class="location"]/a/text()')[-2].extract()
        item["classNum"] = len(response.xpath('//*[@class="location"]/a')) - 1
        item["specificName"] = response.xpath('//*[@class="location"]/a/text()')[-1].extract()
        item["title"] = response.xpath('/html/body/div/div/div/h1/text()').extract_first()
        item["source"] = '大众养生网'
        item["sourceUrl"] = response.url
        item['imageUrls'] = response.xpath('//*[@style="text-align:center;"]/a/img/@src').extract() #提取图片链接
        if len(response.xpath('//*[@style="text-align:center;"]/a/img/@src').extract()) == 0:
            item['imageUrls'] = response.xpath('//*[@style="text-align:center;"]/img/@src').extract()
        item["time"] = response.xpath('//*[@class="info"]/span/text()')[1].extract().split(':')[1].split(' ')[0]

        text_list = response.xpath('//*[@class="content_text"]/*')

        item["text"] = processText(text_list)

        if len(response.xpath('//*[@class=" paging"]/a/text()')) > 0:
            if response.xpath('//*[@class=" paging"]/a/text()')[-1].extract().encode('utf-8') == '下一页':
                n_url = 'http://www.cndzys.com/' + response.xpath('//*[@class=" paging"]/a/@href')[-1].extract()
                yield scrapy.Request(url=n_url, callback=self.parse_info)
        yield item

        # 在最后一个孩子哪儿判断是否需要爬取下一页，如果代码没有执行到这儿，那么说明下一页的时间已经是无效的时间了
        if item['is_final_child'] and item['next_father_url'] is not None:
            yield scrapy.Request(url=item['next_father_url'], callback=self.parse)
