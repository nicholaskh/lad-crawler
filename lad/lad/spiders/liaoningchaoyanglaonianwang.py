#coding=utf-8
import scrapy
import re

from ..items import YanglaoItem
from ..spiders.beautifulSoup import processText, processImgSep
from datetime import datetime
from .basespider import BaseTimeCheckSpider

class newsSpider(BaseTimeCheckSpider):
    name = 'liaoningchaoyanglaonianwang'
    start_urls = ['http://www.cylnw.com/news.asp?lb=6&page=1']

    def parse(self, response):
        should_deep = True
        times_ori= response.xpath('/html/body/table[3]/tr/td/table[2]/tr/td[1]/table/tr/td/table/tr/td/table/tr/td/table/tr[3]/td/table//tr/td/text()').extract()
        times_ori2 = []
        times = []
        for each in times_ori:
            if '/' in each:
                times_ori2.append(each.split(' ')[0])
        for each in times_ori2:
            times.append(each.replace('/','-'))
        if len(times) == 0:
            should_deep =False

        #是相对链接
        urls_ori = response.xpath('/html/body/table[3]/tr/td/table[2]/tr/td[1]/table/tr/td/table/tr/td/table/tr/td/table/tr[3]/td/table//tr/td[2]/span/a/@href').extract()
        urls = []
        for each in urls_ori:
            url = 'http://www.cylnw.com/' + each
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
            #url = 'http://www.ahllb.cn' + url
            valid_child_urls.append(url)

        next_requests = list()
        # if should_deep:
        #     #maxPageNum = int(response.xpath('//div[@class="pagenum_label"]//dd/p/text()').extract()[0].strip())
        #     if '_' not in response.url:
        #         currentPageNum = 1
        #     else:
        #         currentPageNum = int(response.url.split('_')[-1])
        #
        #     nextPageNum = currentPageNum + 1
        #     if nextPageNum > 5:
        #         return
        #
        #     next_url = 'http://www.yanglao.com.cn/article_' + str(nextPageNum)
        #     req = scrapy.Request(url=next_url, callback=self.parse)
        #     yield req

        for index, temp_url in enumerate(valid_child_urls):
            req = scrapy.Request(url=temp_url, callback=self.parse_info)
            m_item = YanglaoItem()
            #m_item['title'] = titles[index]
            m_item['time'] = times[index]
            m_item['className'] = '政策法规'
            req.meta['item'] = m_item
            yield req

    def parse_info(self, response):
        item = response.meta['item']

        item["source"] = "辽宁朝阳老年网"

        # title_ori =  response.xpath('//div[@class="w96"]/h1/text() | //div[@class="w96"]/h1/span/text()').extract()
        # title =''
        # for each in title_ori:
        #     title = title + each
        title = response.xpath('//div[@class="bt"]/text()').extract()[0]
        if len(title) == 0:
            return
        item["title"] = title


        item["sourceUrl"] = response.url
        # 修改了text_list
        #text_list = response.xpath('//*[@id="ivs_content"]/p/text() | //*[@id="ivs_content"]/p//font/text()')
        text_list = response.xpath('//div[@class="hg20"]/*')
        text = processText(text_list)
        item["text"] = text

        text_list = response.xpath('//div[@class="hg20"]/*')
        img_list = processImgSep(text_list)
        final_img_list = []
        for img in img_list:
            if 'http' not in img:
                img = 'http://www.cylnw.com' + img
            final_img_list.append(img)

        item['imageUrls'] = final_img_list
        if 'http://www.cylnw.com/webedit/sysimage/file/doc.gif' in final_img_list:
            return
        if text.strip() == "" and len(img_list) == 0:
            return

        yield item
