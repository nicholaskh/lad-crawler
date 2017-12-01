#coding=utf-8
import scrapy
import re

from ..items import YangshengwangItem
from ..spiders.beautifulSoup import processText, processImgSep
from datetime import datetime
from basespider import BaseTimeCheckSpider

class NewsSpider(BaseTimeCheckSpider):

    name = "99yangshengwangnew"
    # 健康新知
    dict_news = {
        'yszx/rdzx':'热点资讯&养生资讯',
        'yszx/ysxd':'瘦身减肥&养生资讯',
        'yszx/mrys':'美容养生&养生资讯',
        'yszx/ysbk':'健康疾病&养生资讯',
        'yszx/ystk':'养生图库&养生资讯',
        'ysrq/nrys':'男性保健&保健人群',
        'ysrq/nvrys':'女性保健&保健人群',
        'ysrq/lrys':'老人保健&保健人群',
        'ysrq/rtys':'儿童保健&保健人群',
        'ysrq/mrys':'名人保健&保健人群',
        'zyys/zycs':'中医常识&中医养生',
        'zyys/zjys':'针灸养生&中医养生',
        'zyys/jlys':'经络养生&中医养生',
        'zyys/zyjq':'中医技巧&中医养生'
    }
    start_urls = ['http://www.99ysw.cn/%s/' % x for x in dict_news.keys()]

    def parse(self, response):

        next_url = None
        if len(response.xpath('//*[@class="con_left"]')) == 10:
            #判断是否是最后一页,不是的话执行下面逻辑
            if 'html' in response.url:
                num = int(response.url.split('_')[1].split('.')[0])
                next_url = response.url.split('_')[0] + '_' + str(num + 1) + ".html"
            else:
                next_url = response.url + 'index_2.html'

        child_urls = response.xpath('//*[@class="con_left"]/div/a/@href')
        for infoDiv in child_urls[:-1]:
            n_url = 'http://www.99ysw.cn' + infoDiv.extract()
            child_request = scrapy.Request(url=n_url, callback=self.parse_info)
            m_item = YangshengwangItem()
            m_item['is_final_child'] = False
            key_word = response.url.split('/')[3]+'/'+response.url.split('/')[4]
            total_str = self.dict_news[key_word]
            m_item["classNum"] = 2
            m_item['specificName'] = total_str.split('&')[0]
            m_item["className"] = total_str.split('&')[1]
            child_request.meta['item'] = m_item
            yield child_request

        # 特殊处理最后一个，通过request的meta传递信息
        final_child_url = 'http://www.99ysw.cn' + child_urls[-1].extract()
        final_request = scrapy.Request(url=final_child_url, callback=self.parse_info)
        m_item = YangshengwangItem()
        m_item['is_final_child'] = True
        key_word = response.url.split('/')[3]+'/'+response.url.split('/')[4]
        total_str = self.dict_news[key_word]
        m_item["classNum"] = 2
        m_item['specificName'] = total_str.split('&')[0]
        m_item["className"] = total_str.split('&')[1]
        m_item['next_father_url'] = next_url
        final_request.meta['item'] = m_item
        yield final_request

    def parse_info(self, response):
        item = response.meta['item']
        time = response.xpath('//*[@class="text-center small"]/span/text()').extract_first().encode('utf-8')[15:]

        try:
            time_now = datetime.strptime(time, '%Y-%m-%d %H:%M:%S')
            # 更新将要保存到MONGODB中的时间
            self.update_last_time(time_now)
        except:
            return

        if self.last_time is not None and self.last_time >= time_now:
            print(u'spider: %s 这篇文章已经存在' % self.url)
            return

        item["module"] = "健康资讯"
        item["title"] = response.xpath('//*[@id="content"]/h1/text()').extract_first()
        item["source"] = "99养生网"
        item["sourceUrl"] = response.url
        item["time"] = response.xpath('//*[@class="text-center small"]/span/text()').extract_first().encode('utf-8')[15:]

        text_list = response.xpath('//*[@class="g-content-c f16"]/*')
        item["imageUrls"] = processImgSep(text_list)
        item["text"] = processText(text_list)

        yield item

        # 在最后一个孩子哪儿判断是否需要爬取下一页，如果代码没有执行到这儿，那么说明下一页的时间已经是无效的时间了
        if item['is_final_child'] and item['next_father_url'] is not None:
            yield scrapy.Request(url=item['next_father_url'], callback=self.parse)
