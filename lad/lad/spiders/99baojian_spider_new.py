#coding=utf-8
import scrapy

from ..items import YangshengwangItem
from ..spiders.beautifulSoup import processText
from datetime import datetime
from basespider import BaseTimeCheckSpider

class NewsSpider(BaseTimeCheckSpider):

    name = "99yijinew"
    dict_news = {'zyys/jjys': '2_居家养生','zyys/ysyd': '2_养生有道',
        'zyys/nvys': '2_女人养生','zyys/nvys': '2_男人养生','zyys/sjys': '2_四季养生','zyjb': '中医疾病','changshi': '中医常识'}
    start_urls = ['http://zyk.99.com.cn/%s/' % x for x in dict_news.keys()]
    text = ""

    def parse(self, response):

        next_url = None
        if len(response.xpath('//*[@class="one_list"]/div')) == 15:
            #判断是否是最后一页,不是的话执行下面逻辑
            if 'html' in response.url:
                num = int(response.url.split('_')[2].split('.')[0])
                next_url = response.url.split('_')[0] + '_' + response.url.split('_')[1] + '_' + str(num - 1) + ".html"
            else:
                next_url = 'http://zyk.99.com.cn/zyys/jjys/' + response.xpath('//*[@class="list_page"]/span/a/@href').extract_first()

        child_urls = response.xpath('//*[@class="one_list"]/div/h2/a/@href')
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
        time = response.xpath('//*[@class="title_txt"]/span/text()').extract_first()

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

        item["module"] = "保健常识"
        item["className"] = response.xpath('//*[@class="new_wz"]/span/a/text()')[-2].extract()
        item["classNum"] = 2
        item['specificName'] = response.xpath('//*[@class="new_wz"]/span/a/text()')[-1].extract()
        item["title"] = response.xpath('//*[@class="title_box"]/h1/text()').extract_first()
        item["source"] = "99健康网"
        item["sourceUrl"] = response.url
        if response.xpath('//*[@align="center"]/a/img/@src').extract() is None:
            item["imageUrls"] = ''
        else:
            item["imageUrls"] = response.xpath('//*[@align="center"]/a/img/@src').extract()
        item["time"] = response.xpath('//*[@class="title_txt"]/span/text()').extract_first().split(' ')[0]

        text_list = response.xpath('//*[@class="new_cont detail_con"]/*')

        item["text"] = processText(text_list)

        yield item

        # 在最后一个孩子哪儿判断是否需要爬取下一页，如果代码没有执行到这儿，那么说明下一页的时间已经是无效的时间了
        if item['is_final_child'] and item['next_father_url'] is not None:
            yield scrapy.Request(url=item['next_father_url'], callback=self.parse)
