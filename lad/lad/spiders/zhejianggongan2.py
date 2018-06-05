#coding=utf-8
import scrapy
import re

from ..items import LadItem
from ..spiders.beautifulSoup import processText, processImgSep
from datetime import datetime
from .basespider import BaseTimeCheckSpider

class newsSpider(BaseTimeCheckSpider):
    name = "zhejianggongan2"
    start_urls = ['http://www.zjsgat.gov.cn/jwzx/lszt/ztzl/jgsa/index.html']

    def parse(self, response):
        should_deep = True
        times_ori = response.xpath('//td[@valign="top"]/table[1]').extract()
        times = re.findall(r'<td align="right">(.*?)</td>', str(times_ori))

        #是相对链接
        urls_ori = response.xpath('//td[@valign="top"]/table[1]').extract()
        urls_ori2 = re.findall(r'<a href="(.*?)" target=',str(urls_ori))
        urls = []
        for each in urls_ori2:
            if '.htm' in each:
                url = 'http://www.zjsgat.gov.cn/jwzx/lszt/ztzl/jgsa' + each[1:]
                urls.append(url)
        #titles_ori = response.xpath('//td[@valign="top"]/table[1]').extract()
        #titles = re.findall('title="(.*?)">', str(titles_ori))
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
            #url = 'http://www.hzpolice.gov.cn' + url
            valid_child_urls.append(url)

        next_requests = list()
        if should_deep:
            #maxPageNum = int(response.xpath('//div[@class="pagenum_label"]//dd/p/text()').extract()[0].strip())
            #currentPageNum = int(response.url.split('-')[-1].split('.')[0])
            if 'index.html' in response.url:
                currentPageNum = 0
            else:
                currentPageNum = int(response.url.split('_')[-1].split('.')[0])

            nextPageNum = currentPageNum + 1
            next_url = 'http://www.zjsgat.gov.cn/jwzx/lszt/ztzl/jgsa/index_' + str(nextPageNum) + '.html'
            req = scrapy.Request(url=next_url, callback=self.parse)
            print(req)
            yield req

        for index, temp_url in enumerate(valid_child_urls):
            req = scrapy.Request(url=temp_url, callback=self.parse_info)
            m_item = LadItem()
            #m_item['title'] = titles[index]
            m_item['time'] = times[index]
            m_item['newsType'] = "警事要闻"
            req.meta['item'] = m_item
            yield req

    def parse_info(self, response):
        item = response.meta['item']

        item["city"] = "浙江公安网"
        item["title"] = response.xpath('//td[@valign="top"]/table[2]//td/text()').extract()[3]
        item["sourceUrl"] = response.url
        # 修改了text_list
        #text_list = response.xpath('//*[@id="ivs_content"]/p/text() | //*[@id="ivs_content"]/p//font/text()')
        text_list = response.xpath('//td[@class="d"] | //td[@class="d"]/text()')
        text = processText(text_list)
        item["text"] = text

        text_list = response.xpath('//td[@class="d"]/*')
        img_list = processImgSep(text_list)
        final_img_list = []

        img_url = 'www.zjsgat.gov.cn'
        for i in range(3, len(response.url.split('/')) - 1):
            img_url = img_url + '/' + response.url.split('/')[i]
        for img in img_list:
            if 'http' not in img:
                img = img_url + img[1:]
                img = 'http://' + img
            final_img_list.append(img)
        item['imageUrls'] = final_img_list
        if text.strip() == "" and len(img_list) == 0:
            return

        ####debugging

        import sys
        print(sys.version)
        #####


        yield item
