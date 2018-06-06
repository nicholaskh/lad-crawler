#coding=utf-8
import scrapy
import re

from ..items import YangshengwangItem
from ..spiders.beautifulSoup import processText
from datetime import datetime
from basespider import BaseTimeCheckSpider

class NewsSpider(BaseTimeCheckSpider):

    name = "99yiji2new"
    # 健康新知
    dict_news = {'nxbj':'2_女性保健_保健人群','nanxing':'2_男性保健_保健人群','lrbj':'2_老人保健_保健人群',
                 'cjbj':'2_春季保健_保健资讯','xjbj':'2_夏季保健_保健资讯','qjbj':'2_秋季保健_保健资讯','djbj':'2_冬季保健_保健资讯',
                 'tjgs':'2_调节改善_亚健康','yfcs':'2_预防措施_亚健康','yjkzc':'2_自测_亚健康','jjbj':'2_家居保健_生活保健',
                 'lybj':'1_旅游保健','baojiancao':'1_保健操','shzd':'1_养生指南','slys':'1_营养养生'}
    start_urls = ['http://bj.99.com.cn/%s/' % x for x in dict_news.keys()]

    def parse(self, response):

        next_url = None
        if len(response.xpath('//*[@class="one_list"]/div')) == 15:
            #判断是否是最后一页,不是的话执行下面逻辑
            if 'htm' in response.url:
                num = int(response.url.split('-')[1].split('.')[0])
                next_url = response.url.split('-')[0] + '-' + str(num - 1) + ".htm"
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
                m_item['specificName'] = total_str.split('_')[1]
                m_item["className"] = total_str.split('_')[2]
            else:
                m_item["className"] = total_str.split('_')[1]
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
            m_item['specificName'] = total_str.split('_')[1]
            m_item["className"] = total_str.split('_')[2]
        else:
            m_item["className"] = total_str.split('_')[1]
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
