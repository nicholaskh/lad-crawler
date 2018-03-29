#coding=utf-8
import scrapy
import re

from ..items import LadItem
from ..spiders.beautifulSoup import processText, processImgSep
from datetime import datetime
from .basespider import BaseTimeCheckSpider

class newsSpider(BaseTimeCheckSpider):
    name = "gonganbu2"
    # dict_commens = {
    #     'n2253535/index.html': '公安要闻',
    #     'n2253543/index.html': '警方提示'
    # }
    # start_urls = ['http://www.mps.gov.cn/n2253534/%s' % x for x in dict_commens.keys()]
    start_urls = ['http://www.mps.gov.cn/n2253534/n2253543/index.html']

    def parse(self, response):
        should_deep = True
        times_ori = response.xpath('//*[@id="comp_3497341"]/dl//span/text()').extract()
        times = []
        #对时间进行特殊处理，去掉括号和空格
        for time_each in times_ori:
            times.append(time_each[2:-2])
        #是相对链接
        urls_ori = response.xpath('//*[@id="comp_3497341"]/dl//a/@href').extract()
        urls = []
        #变为绝对链接，下面的变化代码被注释
        for url_each in urls_ori:
            url = "http://www.mps.gov.cn" + url_each[5:]
            urls.append(url)

        valid_child_urls = list()

        for time, url in zip(times, urls):
            try:
                time_now = datetime.strptime(time.strip(), '%Y-%m-%d')
                self.update_last_time(time_now)
            except:
                print("Something Wrong")
                break

            if self.last_time is not None and self.last_time >= time_now:
                should_deep = False
                break
            # 变成绝对url
            # url = 'http://www.hzpolice.gov.cn' + url
            valid_child_urls.append(url)

        #下一页的新闻
        next_requests = list()
        if should_deep:
            data_ori = response.xpath('//*[@id="pag_3497341"]').extract()[0]
            maxPageNum = re.findall('maxPageNum = (.*?);', data_ori)[0]
            next_url = "http://www.mps.gov.cn/n2253534/n2253543/index_3497341_" + str(int(maxPageNum)-1) + ".html"
            req = scrapy.Request(url = next_url, callback=self.parse_deeperpage)
            yield req
            # page_num = int(response.url.split('&')[-1].split('=')[-1])
            # real_page = int(response.xpath('//input[@name="dd_currentPage"]/@value').extract_first())
            # #避免进入多余的页
            # if real_page != page_num:
            #     return
            # page_num = page_num + 1
            # next_url = response.url.split('&')[0] + "&page=" + str(page_num)
            # next_requests.append(scrapy.Request(url=next_url, callback=self.parse))

        #准备处理一条具体新闻
        for index, temp_url in enumerate(valid_child_urls):
            req = scrapy.Request(url=temp_url, callback=self.parse_info)
            m_item = LadItem()
            m_item['time'] = times[index]
            m_item['newsType'] = "警事要闻"
            req.meta['item'] = m_item
            yield req


            # class LadItem(scrapy.Item):
            #     collection = settings['COLLECTION_SECURITY']
            #     title = scrapy.Field()
            #     newsType = scrapy.Field()
            #     time = scrapy.Field()
            #     text = scrapy.Field()
            #     city = scrapy.Field()
            #     sourceUrl = scrapy.Field()  # 来源网址
            #     is_final_child = scrapy.Field()
            #     next_father_url = scrapy.Field()
            #     sourceUrl = scrapy.Field()
            #     imageUrls = scrapy.Field()  # 图片的链接
            #     num = scrapy.Field()  # 随机数
            # req = scrapy.Request(url=temp_url, callback=self.parse_info)
            #
            # hit_time = times[index]
            # m_item = LadItem()
            # m_item['time'] = hit_time.strip()
            # key_word = response.url.split('&')[0].split('=')[-1] + "&page=1"
            # news_type = self.dict_commens[key_word]
            # m_item['newsType'] = news_type
            # # 相当于在request中加入了item这个元素
            # req.meta['item'] = m_item
            # next_requests.append(req)

        # for req in next_requests:
        #     yield req


    def parse_deeperpage(self, response):
        should_deep1 = True
        times_ori1 = response.xpath('/html/body/dl//dd/span/text()').extract()
        times = []
        # 对时间进行特殊处理，去掉括号和空格
        for time_each in times_ori1:
            times.append(time_each[2:-2])
        # 是相对链接
        urls_ori1 = response.xpath('/html/body/dl//dd/a/@href').extract()
        urls = []
        # 变为绝对链接，下面的变化代码被注释
        for url_each in urls_ori1:
            url = "http://www.mps.gov.cn" + url_each[5:]
            urls.append(url)

        valid_child_urls = list()

        for time, url in zip(times, urls):
            try:
                time_now = datetime.strptime(time.strip(), '%Y-%m-%d')
                self.update_last_time(time_now)
            except:
                print("Something Wrong")
                break

            if self.last_time is not None and self.last_time >= time_now:
                should_deep1 = False
                break
            # 变成绝对url
            # url = 'http://www.hzpolice.gov.cn' + url
            valid_child_urls.append(url)

        # 下一页的新闻
        next_requests = list()
        if should_deep1:
            current_page = int(response.url.split('_')[-1].split('.')[0])
            if current_page >=2:
                next_url = "http://www.mps.gov.cn/n2253534/n2253535/index_5097045_" + str(current_page - 1) + ".html"
                req = scrapy.Request(url=next_url, callback=self.parse_deeperpage)
                yield req
            # page_num = int(response.url.split('&')[-1].split('=')[-1])
            # real_page = int(response.xpath('//input[@name="dd_currentPage"]/@value').extract_first())
            # #避免进入多余的页
            # if real_page != page_num:
            #     return
            # page_num = page_num + 1
            # next_url = response.url.split('&')[0] + "&page=" + str(page_num)
            # next_requests.append(scrapy.Request(url=next_url, callback=self.parse))

        # 准备处理一条具体新闻
        for index, temp_url in enumerate(valid_child_urls):
            req = scrapy.Request(url=temp_url, callback=self.parse_info)
            m_item = LadItem()
            m_item['time'] = times[index]
            m_item['newsType'] = "警事要闻"
            req.meta['item'] = m_item
            yield req
            # req = scrapy.Request(url=temp_url, callback=self.parse_info)
            #
            # hit_time = times[index]
            # m_item = LadItem()
            # m_item['time'] = hit_time.strip()
            # key_word = response.url.split('&')[0].split('=')[-1] + "&page=1"
            # news_type = self.dict_commens[key_word]
            # m_item['newsType'] = news_type
            # # 相当于在request中加入了item这个元素
            # req.meta['item'] = m_item
            # next_requests.append(req)

            # for req in next_requests:
            #     yield req


    def parse_info(self, response):
        item = response.meta['item']

        item["city"] = "中华人民共和国公安部"

        title_ori = response.xpath('/html/body/div/div[4]//h1/text()').extract()
        title = ""
        for title_each in title_ori:
            title = title + title_each
            title = title + " "

        item["title"] = title[:-1]
        item["sourceUrl"] = response.url
        # 修改了text_list
        text_list = response.xpath('//*[@id="ztdx"]/* | //*[@id="ztdx"]//text()')
        text = processText(text_list)
        item["text"] = text

        text_list = response.xpath('//*[@id="ztdx"]/* | //*[@id="ztdx"]//text()')

        img_list = processImgSep(text_list)
        final_img_list = []
        for img in img_list:
            if 'http' not in img:
                img = 'http://www.mps.gov.cn' + img[8:]
            final_img_list.append(img)
        item['imageUrls'] = final_img_list
        if text.strip() == "" and len(img_list) == 0:
            return

        yield item
