#coding=utf-8
import scrapy
import re

from ..items import YanglaoItem
from ..spiders.beautifulSoup import processText, processImgSep
from datetime import datetime
from .basespider import BaseTimeCheckSpider

class newsSpider(BaseTimeCheckSpider):
    name = "fengwang"
    start_urls = ['http://www.laoren.com/ylzx/zc/index.shtml',
'http://www.laoren.com/ylzx/ylj/index.shtml',
'http://www.laoren.com/ylzx/ylbx/index.shtml',
'http://www.laoren.com/ylzx/xf/index.shtml',
'http://www.laoren.com/ylzx/jj/index.shtml',
'http://www.laoren.com/ylzx/ylcy/index.shtml',
'http://www.laoren.com/ylzx/kclr/index.shtml'
]

    def parse(self, response):
        should_deep = True
        times = response.xpath('//div[@class="lbUl"]/ul//span/text()').extract()
        if len(times) == 0:
            should_deep =False
        # times_ori = response.xpath('/html/body/div[3]/div[1]/table[2]//span/text()').extract()
        # for each in times_ori:
        #     time_ori = each[1:-1].split('/')
        #     time_ori2 = ''
        #     for i in range(0,len(time_ori)):
        #         time_ori2 = time_ori2 + time_ori[i] + '-'
        #     times.append(time_ori2[:-1])

        #是相对链接
        urls = response.xpath('//div[@class="lbUl"]/ul//a/@href').extract()
        # urls = []
        # for each in urls_ori:
        #     if 'List_' not in each:
        #         url = 'http://shebao.southmoney.com' + each
        #         urls.append(url)
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
            if 'index_' in response.url:
                currentPageNum =int(response.url.split('_')[-1].split('.')[0])
            else:
                currentPageNum = 1

            nextPageNum = currentPageNum + 1
            if nextPageNum > 11:
                return

            url_split = response.url.split('/')
            next_url = 'http://www.laoren.com/'
            for i in range(3,len(url_split)-1):
                next_url = next_url + url_split[i] + '/'

            next_url = next_url + 'index_' + str(nextPageNum) + '.shtml'
            req = scrapy.Request(url=next_url, callback=self.parse)
            yield req

        for index, temp_url in enumerate(valid_child_urls):
            req = scrapy.Request(url=temp_url, callback=self.parse_info)
            m_item = YanglaoItem()
            #m_item['title'] = titles[index]
            m_item['time'] = times[index]
            #m_item['className'] = '养老保险'
            req.meta['item'] = m_item
            yield req

    def parse_info(self, response):
        item = response.meta['item']

        item["source"] = "枫网"

        if response.xpath('//span[@class="gray2"]/a[3]/text()').extract()[0] == u'养老政策':
            item['className'] = '政策法规'
        elif response.xpath('//span[@class="gray2"]/a[3]/text()').extract()[0] == u'养老金':
            item['className'] = '养老金'
        elif response.xpath('//span[@class="gray2"]/a[3]/text()').extract()[0] == u'养老保险':
            item['className'] = '养老保险'
        else:
            item['className'] = '养老频道'

        item["title"] = response.xpath('//h1[@class="blue3 taC wryh"]/a/text()').extract()[0]
        item["sourceUrl"] = response.url
        # 修改了text_list
        #text_list = response.xpath('//*[@id="ivs_content"]/p/text() | //*[@id="ivs_content"]/p//font/text()')
        text_list = response.xpath('//div[@class="viewCont"]/*')
        text = processText(text_list)
        item["text"] = text

        text_list = response.xpath('//div[@class="viewCont"]/*')
        img_list = processImgSep(text_list)
        final_img_list = []
        for img in img_list:
            if 'http' not in img:
                img = '' + img
            final_img_list.append(img)

        item['imageUrls'] = final_img_list
        if text.strip() == "" and len(img_list) == 0:
            return

        yield item
