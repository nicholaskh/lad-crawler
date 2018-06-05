# coding=utf-8
import scrapy
import re

from ..items import YanglaoItem
from ..spiders.beautifulSoup import processText, processImgSep
from datetime import datetime
from .basespider import BaseTimeCheckSpider


class newsSpider(BaseTimeCheckSpider):
    name = "guangzhoulaolingwang2"
    start_urls = ['http://gzll.gzmz.gov.cn/gzsllgzwyhbgs/llyw/list.shtml']

    def parse(self, response):
        should_deep = True
        times = response.xpath('//div[@class="news_list"]/ul/li[position()>1]/span/text()').extract()
        if len(times) == 0:
            should_deep = False
        # times = []
        # for each in times_ori:
        #     if '-' in each:
        #         times.append(each.strip())

        # 是相对链接
        urls_ori = response.xpath('//div[@class="news_list"]/ul/li[position()>1]/a/@href').extract()
        urls =[]
        for each in urls_ori:
            url = 'http://gzll.gzmz.gov.cn' + each[5:]
            urls.append(url)
        # titles_ori = response.xpath('//td[@valign="top"]/table[1]').extract()
        # titles = re.findall('title="(.*?)">', str(titles_ori))
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

        next_requests = list()
        # if should_deep:
        #     #maxPageNum = int(response.xpath('//div[@class="pagenum_label"]//dd/p/text()').extract()[0].strip())
        #     currentPageNum = int(response.url.split('=')[-1])
        #     nextPageNum = currentPageNum + 1
        #     if nextPageNum > 3:
        #         return
        #
        #     next_url = 'http://www.theold.net/inter/pol/?page=' + str(nextPageNum)
        #     req = scrapy.Request(url=next_url, callback=self.parse)
        #     yield req

        for index, temp_url in enumerate(valid_child_urls):
            req = scrapy.Request(url=temp_url, callback=self.parse_info)
            m_item = YanglaoItem()
            # m_item['title'] = titles[index]
            m_item['time'] = times[index]
            m_item['className'] = '老龄新闻'
            req.meta['item'] = m_item
            yield req

    def parse_info(self, response):
        item = response.meta['item']

        item["source"] = "广州老龄网"
        item["title"] = response.xpath('//h2[@class="info_title"]/text()').extract()[0].strip()
        item["sourceUrl"] = response.url
        # 修改了text_list
        # text_list = response.xpath('//*[@id="ivs_content"]/p/text() | //*[@id="ivs_content"]/p//font/text()')
        text_list = response.xpath('//div[@class="info_cont"]/*')
        text = processText(text_list)
        item["text"] = text

        text_list = response.xpath('//div[@class="info_cont"]/*')
        img_list = processImgSep(text_list)
        final_img_list = []
        img_url = 'gzll.gzmz.gov.cn'
        for i in range(3, len(response.url.split('/')) - 1):
            img_url = img_url + '/' + response.url.split('/')[i]
        img_url = img_url + '/'
        for img in img_list:
            if 'http' not in img:
                img = img_url + img
                img = 'http://' + img
            final_img_list.append(img)
        item['imageUrls'] = final_img_list
        if text.strip() == "" and len(img_list) == 0:
            return

        yield item
