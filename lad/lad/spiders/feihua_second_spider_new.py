#coding=utf-8
import scrapy
import re

from ..items import YangshengwangItem
from ..spiders.beautifulSoup import processText, processImg
from datetime import datetime
from basespider import BaseTimeCheckSpider

class newsSpider(BaseTimeCheckSpider):
    name = "feihua2new"
    dict_news = {'cjbj': '6534_春季保健&四季保健', 'xjbj': '6535_夏季保健&四季保健','qjbj': '6539_秋季保健&四季保健',
        'djbj': '6536_冬季保健&四季保健','nvx': '6531_女性保健&保健人群','bgs': '6537_白领保健&保健人群','nxbj': '6530_男性保健&保健人群',
        'lrbj': '6532_老人保健&保健人群','ert': '6533_儿童保健&保健人群'}
    start_urls = ['http://care.fh21.com.cn/%s/' % x for x in dict_news.keys()]

    def parse(self, response):

        should_deep = True

        times = response.xpath('//*[@class="ma-modone-right-time"]/text()').extract()
        urls = response.xpath('//*[@class="ma-modone-right fl"]/a/@href').extract()
        key_word = re.search('cn/(.+)/', response.url).group(1)

        valid_child_urls = list()

        for time, url in zip(times, urls):
            try:
                time_now = datetime.strptime(time.strip(), '%Y-%m-%d %H:%M')
                self.update_last_time(time_now)
            except:
                break

            if self.last_time is not None and self.last_time >= time_now:
                should_deep = False
                break

            valid_child_urls.append('http://care.fh21.com.cn' + url)

        next_requests = list()
        if should_deep:
            # 表示有新的url
            # 翻页
            if response.xpath('//*[@class="wrap-list-paging mt-20"]/p/a/text()').extract()[-2] == '下一页':
                #判断是否是最后一页,不是的话执行下面逻辑
                if len(response.url) == 29:
                    next_url = response.url + 'list_' + self.dict_news[key_word].split('_')[0] + '_2.html'
                else:
                    num = int(response.url.split('_')[2][0])
                    next_url = response.url.split(str(num) + ".html")[0] + str(num + 1) + ".html"
                next_requests.append(scrapy.Request(url=next_url, callback=self.parse))

        for index, temp_url in enumerate(valid_child_urls):
            req = scrapy.Request(url=temp_url, callback=self.parse_info)

            hit_time = times[index]
            m_item = YangshengwangItem()
            m_item['time'] = hit_time
            m_item["className"] = self.dict_news[key_word].split('&')[-1]
            m_item["specificName"] = self.dict_news[key_word].split('&')[0].split('_')[-1]
            # 相当于在request中加入了item这个元素
            req.meta['item'] = m_item
            next_requests.append(req)

        for req in next_requests:
            yield req

    def parse_info(self, response):
        item = response.meta['item']

        item["module"] = "健康资讯"
        item["classNum"] = 2
        item["title"] = response.xpath('//*[@class="arti-head"]/h2/text()').extract_first()
        item["source"] = "飞华保健网"
        item["sourceUrl"] = response.url
        item["imageUrls"] = processImg(response.xpath('//*[@class="arti-content"]').extract_first())
        item["time"] = response.xpath('/html/body/div[4]/div/div[1]/div[2]/div[1]/div/span/text()').extract_first().strip().split(' ')[1]

        text_list = response.xpath('//*[@class="arti-content"]/*')

        item["text"] = processText(text_list)

        yield item
