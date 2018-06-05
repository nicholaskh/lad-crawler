#coding=utf-8
import scrapy
import re

from ..items import YanglaoItem
from ..spiders.beautifulSoup import processText, processImgSep
from datetime import datetime
from .basespider import BaseTimeCheckSpider

class newsSpider(BaseTimeCheckSpider):
    name = "shebaopindao"
    start_urls = ['http://www.wifi03.com/news/list_8.html']

    def parse(self, response):
        should_deep = True
        times = []
        times_ori = response.xpath('//div[@class="addi"]/text()').extract()
        for each in times_ori:
            times.append(each.strip().split(' ')[0])

        #是相对链接
        urls_ori = response.xpath('//*[@id="newsList"]/div[1]/dl/dd//h4/a/@href').extract()
        urls = []
        for each in urls_ori:
            ID = each.split('/')[-1].split('.')[0]
            url = 'http://www.wifi03.com/wapNews.asp?dataID=' + ID
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
            if 'list_8_' in response.url:
                currentPageNum = int(response.url.split('_')[-1].split('.')[0])
            else:
                currentPageNum = 1;
            nextPageNum = currentPageNum + 1
            if nextPageNum > 15:
                return
            else:
                next_url = 'http://www.wifi03.com/news/list_8_' + str(nextPageNum) + '.html'
                req = scrapy.Request(url=next_url, callback=self.parse)
                yield req

        for index, temp_url in enumerate(valid_child_urls):
            req = scrapy.Request(url=temp_url, callback=self.parse_info)
            m_item = YanglaoItem()
            #m_item['title'] = titles[index]
            m_item['time'] = times[index].split(' ')[0]
            m_item['className'] = "养老保险"
            req.meta['item'] = m_item
            yield req

    def parse_info(self, response):
        item = response.meta['item']

        item["source"] = "社保频道"
        item["title"] = response.xpath('//h1[@class="fonth2"]/text()').extract()[0]
        item["sourceUrl"] = response.url
        # 修改了text_list
        #text_list = response.xpath('//*[@id="ivs_content"]/p/text() | //*[@id="ivs_content"]/p//font/text()')
        text_list = response.xpath('//div[@class="wapContent"]/*')
        text = processText(text_list)
        item["text"] = text

        text_list = response.xpath('//div[@class="wapContent"]/*')
        img_list = processImgSep(text_list)
        final_img_list = []
        for img in img_list:
            if 'http' not in img:
                img = 'http://www.wifi03.com/' + img
            final_img_list.append(img)
        item['imageUrls'] = final_img_list
        if text.strip() == "" and len(img_list) == 0:
            return

        yield item