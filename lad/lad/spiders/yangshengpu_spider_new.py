#coding=utf-8
import scrapy
import re

from ..items import YangshengwangItem
from ..spiders.beautifulSoup import processText, processImgSep
from datetime import datetime
from basespider import BaseTimeCheckSpider

class newsSpider(BaseTimeCheckSpider):
    name = "yangshengpunew"
    dict_commens = {
        'zy/zhong-yao': '2中药材大全&中药养生',
        'zy/zhongyaofang': '2中医药方大全&中药养生',
        'zy/pianfangdaquan': '2偏方大全&中药养生',
        'zy/zhongyaopaojiao': '2中药泡脚-药浴&中药养生',
        'qjys': '2春季保健&四季保健',
        'xjys': '2夏季保健&四季保健',
        'qiujiys': '2秋季保健&四季保健',
        'djys': '2冬季保健&四季保健',
        'zyys': '1中医养生',
        'slys': '1饮食养生',
        'jbdq': '1疾病大全',
        'bjzs': '1保健知识',
        'jiankangchangshi': '1健康常识',
        'jingluoys': '1经络穴位'
    }
    start_urls = ['http://www.yangshengpu.com/%s/' % x for x in dict_commens.keys()]

    def parse(self, response):
        should_deep = True
        times = response.xpath('//div[@class="listbox"]/ul/li/span/text()[2]').extract()
        #是相对链接
        urls = response.xpath('//div[@class="listbox"]/ul/li/a[@class="title"]/@href').extract()

        valid_child_urls = list()

        for time, url in zip(times, urls):
            try:
                #去掉双引号
                final_time = time
                time_now = datetime.strptime(final_time, '%Y-%m-%d %H:%M:%S')
                self.update_last_time(time_now)
            except:
                print("Something Wrong")
                break

            if self.last_time is not None and self.last_time >= time_now:
                should_deep = False
                break
            # 变成绝对url
            url = 'http://www.yangshengpu.com' + url
            valid_child_urls.append(url)

        next_requests = list()
        if should_deep:
            pagelist_text = response.xpath('//ul[@class="pagelist"]/li/a/text()').extract()
            pagelist_href = response.xpath('//ul[@class="pagelist"]/li/a/@href').extract()
            for text, url in zip(pagelist_text,pagelist_href):
                if text == "下一页":
                    key_word = re.search('com/(.+)/', response.url).group(1)
                    next_url = 'http://www.yangshengpu.com/' + key_word + '/' + url
                    print('**********')
                    print(next_url)
                    next_requests.append(scrapy.Request(url=next_url, callback=self.parse))

        for index, temp_url in enumerate(valid_child_urls):
            req = scrapy.Request(url=temp_url, callback=self.parse_info)

            hit_time = times[index]
            m_item = YangshengwangItem()
            m_item['time'] = hit_time
            key_word = re.search('com/(.+)/', response.url).group(1)
            total_str = self.dict_commens[key_word]
            print(total_str)
            if total_str[0] == '1':
                m_item["classNum"] = 1
                m_item["className"] = total_str[1:]
            else:
                m_item["classNum"] = 2
                m_item["className"] = total_str.split('&')[1]
                m_item["specificName"] = total_str.split('&')[0][1:]
            # 相当于在request中加入了item这个元素
            req.meta['item'] = m_item
            next_requests.append(req)

        for req in next_requests:
            yield req

    def parse_info(self, response):
        item = response.meta['item']

        item["module"] = "健康资讯"
        item["title"] = response.xpath('//div[@class="title"]/h1/text()').extract_first()
        item["source"] = "养生铺"
        item["sourceUrl"] = response.url
        # 修改了text_list
        text_list = response.xpath('//div[@class="content"]/table/tr/td/*')
        if len(text_list) == 0:
            text_list = response.xpath('//*[@class="article"]/*')

        item["text"] = processText(text_list)
        img_list = processImgSep(text_list)
        final_img_list = []
        for img in img_list:
            if 'yangshengpu' not in img:
                img = 'http://www.yangshengpu.com' + img
            final_img_list.append(img)
        item['imageUrls'] = final_img_list

        yield item
