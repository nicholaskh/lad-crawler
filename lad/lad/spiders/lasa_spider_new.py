#coding=utf-8
import scrapy

from ..items import LadItem
from ..spiders.beautifulSoup import processText
from datetime import datetime
from basespider import BaseTimeCheckSpider

class NewsSpider(BaseTimeCheckSpider):

    name = "lasanew"
    districts = ['jingwuxinwen', 'yinshijingxun']
    start_urls = ['http://ga.lasa.gov.cn/%s/' % x for x in districts]

    def parse(self, response):

        next_url = None
        if len(response.xpath('//*[@class="fixed"]/div/h4/a/@href')) == 20:
            #判断是否是最后一页,不是的话执行下面逻辑
            if len(response.url) <= 36:
                next_url = response.url[0:len(response.url) - 1] + "?pageIndex=2"
            else:
                num = int(response.url.split('=')[1]) + 1
                next_url = response.url.split('pageIndex')[0] + "pageIndex=" + '%s' %num

        child_urls = response.xpath('//*[@class="fixed"]/div/h4/a/@href')
        for infoDiv in child_urls[:-1]:
            n_url = "http://ga.lasa.gov.cn" + infoDiv.extract()
            child_request = scrapy.Request(url=n_url, callback=self.parse_info)
            m_item = LadItem()
            m_item['is_final_child'] = False
            child_request.meta['item'] = m_item
            yield child_request

        # 特殊处理最后一个，通过request的meta传递信息
        final_child_url = "http://ga.lasa.gov.cn" + child_urls[-1].extract()
        final_request = scrapy.Request(url=final_child_url, callback=self.parse_info)
        m_item = LadItem()
        m_item['is_final_child'] = True
        m_item['next_father_url'] = next_url
        final_request.meta['item'] = m_item
        yield final_request

    def parse_info(self, response):
        item = response.meta['item']
        c = response.xpath('/html/body/section/section/div/h6/b[3]/span/text()').extract_first().split(' ')[0].split('/')
        item["time"] = c[0] + '-' + c[1] + '-' + c[2]
        time = response.xpath('/html/body/section/section/div/h6/b[3]/span/text()').extract_first()

        try:
            time_now = datetime.strptime(time, '%Y/%m/%d %H:%M:%S')
            print(time_now)
            # 更新将要保存到MONGODB中的时间
            self.update_last_time(time_now)
        except:
            print("Something wrong")
            return

        if self.last_time is not None and self.last_time >= time_now:
            print(u'spider: %s 这篇文章已经存在' % self.url)
            return
        # next_requests = list()
        #if should_deep:
        # 表示有新的url
        item["city"] = "拉萨公安网"
        item['newsType'] = '警事要闻'
        item["title"] = response.xpath('/html/body/section/section/div/h2/text()').extract_first()
        c = response.xpath('/html/body/section/section/div/h6/b[3]/span/text()').extract_first().split(' ')[0].split('/')
        item["time"] = c[0] + '-' + c[1] + '-' + c[2]

        text_list = response.xpath('//*[@class="main_para_txt"]/*')
        item["text"] = processText(text_list)

        yield item

        # 在最后一个孩子哪儿判断是否需要爬取下一页，如果代码没有执行到这儿，那么说明下一页的时间已经是无效的时间了
        if item['is_final_child'] and item['next_father_url'] is not None:
            yield scrapy.Request(url=item['next_father_url'], callback=self.parse)
