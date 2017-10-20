#coding=utf-8
import scrapy
import re

from ..items import YangshengwangItem
from ..spiders.beautifulSoup import processText
from datetime import datetime
from basespider import BaseTimeCheckSpider

class NewsSpider(BaseTimeCheckSpider):

    name = "99yijinew"
    dict_news = {'zyys/jjys': '2_居家养生&中医养生','zyys/ysyd': '2_养生有道&中医养生','zyys/sjys': '2_四季养生&中医养生','zyjb': '1_中医疾病','changshi': '1_中医常识'}
    start_urls = ['http://zyk.99.com.cn/%s/' % x for x in dict_news.keys()]

    def parse(self, response):

        next_url = None
        if len(response.xpath('//*[@class="one_list"]/div')) == 15:
            #判断是否是最后一页,不是的话执行下面逻辑
            if 'html' in response.url:
                num = int(response.url.split('_')[2].split('.')[0])
                next_url = response.url.split('_')[0] + '_' + response.url.split('_')[1] + '_' + str(num - 1) + ".html"
            else:
                next_url = response.url + response.xpath('//*[@class="list_page"]/span/a/@href').extract_first()

        child_urls = response.xpath('//*[@class="one_list"]/div/h2/a/@href')
        for infoDiv in child_urls[:-1]:
            n_url = infoDiv.extract()
            child_request = scrapy.Request(url=n_url, callback=self.parse_info)
            m_item = YangshengwangItem()
            m_item['is_final_child'] = False
            key_word = re.search('.cn/(.+)/', response.url).group(1)
            total_str = self.dict_news[key_word]
            m_item["classNum"] = total_str.split('_')[0]
            if m_item["classNum"] == "2":
                m_item['specificName'] = total_str.split('_')[-1].split('&')[0]
                m_item["className"] = total_str.split('&')[-1]
            else:
                m_item["className"] = total_str.split('_')[-1]
            m_item['next_father_url'] = next_url
            child_request.meta['item'] = m_item
            yield child_request

        # 特殊处理最后一个，通过request的meta传递信息
        final_child_url = child_urls[-1].extract()
        final_request = scrapy.Request(url=final_child_url, callback=self.parse_info)
        m_item = YangshengwangItem()
        m_item['is_final_child'] = True
        key_word = re.search('.cn/(.+)/', response.url).group(1)
        total_str = self.dict_news[key_word]
        m_item["classNum"] = total_str.split('_')[0]
        if m_item["classNum"] == "2":
            m_item['specificName'] = total_str.split('_')[-1].split('&')[0]
            m_item["className"] = total_str.split('&')[-1]
        else:
            m_item["className"] = total_str.split('_')[-1]
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

        item["module"] = "健康资讯"
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
