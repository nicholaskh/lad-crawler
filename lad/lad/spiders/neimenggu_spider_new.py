#coding=utf-8
import scrapy

from ..items import LadItem
from ..spiders.beautifulSoup import processText
from datetime import datetime
from basespider import BaseTimeCheckSpider

class NewsSpider(BaseTimeCheckSpider):

    name = "neimenggunew"
    start_urls = ['http://www.nmgat.gov.cn/jwzx/afgl/index.html']
    text = ""

    def parse(self, response):

        next_url = None
        if len(response.xpath('//*[@class="gl_r_bj"]/ul/li/a/@href')) == 30:
            #判断是否是最后一页,不是的话执行下面逻辑
            if len(response.url) == 44:
                next_url = 'http://www.nmgat.gov.cn/jwzx/afgl/index_1.html'
            else:
                part_str = response.url.split('/')[5]
                num = int(part_str[6])
                next_url_part = "index_" + str(num + 1) + ".html"
                next_url = 'http://www.nmgat.gov.cn/jwzx/afgl/' + next_url_part

        child_urls = response.xpath('//*[@class="gl_r_bj"]/ul/li')
        for infoDiv in child_urls[:-1]:
            info_url_part = infoDiv.xpath('a/@href').extract_first()
            arry_leng = len(info_url_part.split('/'))
            info_url_sec = info_url_part.split('/')[(arry_leng-2) : arry_leng]
            info_url = info_url_sec[0] + '/' + info_url_sec[1]
            n_url = 'http://www.nmgat.gov.cn/jwzx/afgl/' + info_url
            child_request = scrapy.Request(url=n_url, callback=self.parse_info)
            m_item = LadItem()
            m_item['is_final_child'] = False
            child_request.meta['item'] = m_item
            yield child_request

        # 特殊处理最后一个，通过request的meta传递信息
        info_url_part =  child_urls[-1].xpath('a/@href').extract_first()
        arry_leng = len(info_url_part.split('/'))
        info_url_sec = info_url_part.split('/')[(arry_leng-2) : arry_leng]
        info_url = info_url_sec[0] + '/' + info_url_sec[1]
        n_url = 'http://www.nmgat.gov.cn/jwzx/afgl/' + info_url
        final_request = scrapy.Request(url=n_url, callback=self.parse_info)
        m_item = LadItem()
        m_item['is_final_child'] = True
        m_item['next_father_url'] = next_url
        print (n_url)
        child_request.meta['item'] = m_item
        yield final_request

    def parse_info(self, response):
        item = response.meta['item']
        time = '20' + response.xpath('/html/body/div/div/div[2]/div[3]/div/div/div[3]/div[2]/text()').extract_first().split('|')[1].strip().split('20')[1]

        try:
            time_now = datetime.strptime(time, '%Y-%m-%d %H:%M:%S')
            print(time_now)
            # 更新将要保存到MONGODB中的时间
            self.update_last_time(time_now)
        except:
            print("Something wrong")
            return

        if self.last_time is not None and self.last_time >= time_now:
            print(u'spider: %s 这篇文章已经存在' % self.url)
            return

        item["city"] = '内蒙古'
        item["newsType"] = '警事要闻'
        item["title"] = response.xpath('/html/body/div/div/div[2]/div[3]/div/div/div[2]/text()').extract_first()
        item["time"] = '20' + response.xpath('/html/body/div/div/div[2]/div[3]/div/div/div[3]/div[2]/text()').extract_first().split('|')[1].strip().split('20')[1].split(' ')[0]
        item["sourceUrl"] = response.url

        text_list = response.xpath('/html/body/div/div/div[2]/div[3]/div/div/div[4]/div[1]/div/div/div/p/font')
        if len(text_list) == 0:
            text_list = response.xpath('/html/body/div/div/div[2]/div[3]/div/div/div[4]/div[1]/div/div/p')
        if len(text_list) == 0:
            text_list = response.xpath('/html/body/div/div/div[2]/div[3]/div/div/div[4]/div[1]/div/div/span')
        if len(text_list) == 0:
            text_list = response.xpath('/html/body/div/div/div[2]/div[3]/div/div/div[4]/div[1]/div/div')
        if len(text_list) == 0:
            text_list = response.xpath('/html/body/div/div/div[2]/div[3]/div/div/div[4]/div[1]/div/p/span')
        if len(text_list) == 0:
            text_list = response.xpath('/html/body/div/div/div[2]/div[3]/div/div/div[4]/div[1]/div/span')

        if len(text_list) >= 2:
            for str_slt in text_list:
                if str_slt.xpath('text()').extract_first() is None:
                    self.text = self.text
                else:
                    self.text = self.text + str_slt.xpath('text()').extract_first()
        else:
            if text_list.xpath('text()').extract_first() is None:
                self.text = self.text
            else:
                self.text = self.text + text_list.xpath('text()').extract_first()
        item["text"] = self.text
        self.text = ""

        yield item

        # 在最后一个孩子哪儿判断是否需要爬取下一页，如果代码没有执行到这儿，那么说明下一页的时间已经是无效的时间了
        if item['is_final_child'] and item['next_father_url'] is not None:
            yield scrapy.Request(url=item['next_father_url'], callback=self.parse)
