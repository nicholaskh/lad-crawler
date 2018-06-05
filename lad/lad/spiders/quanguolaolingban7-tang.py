#coding=utf-8
import scrapy
import re

from ..items import YanglaoItem
from ..spiders.beautifulSoup import processText, processImgSep
from datetime import datetime
from .basespider import BaseTimeCheckSpider

class newsSpider(BaseTimeCheckSpider):
    name = "quanguolaolingban7"
    start_urls = ['http://www.cncaprc.gov.cn/channels/792.html']

    def parse(self, response):
        should_deep = True
        times = response.xpath('//div[@class="c1-body"]//div[@class="gray fr"]/text()').extract()
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
        urls = response.xpath('//div[@class="c1-body"]//a/@href').extract()
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
            url = 'http://www.cncaprc.gov.cn' + url
            valid_child_urls.append(url)

        next_requests = list()
        if should_deep:
            #maxPageNum = int(response.xpath('//div[@class="pagenum_label"]//dd/p/text()').extract()[0].strip())
            if '_' in response.url:
                currentPageNum =int(response.url.split('_')[-1].split('.')[0])
            else:
                currentPageNum = 1

            nextPageNum = currentPageNum + 1
            if nextPageNum > 10:
                return

            next_url = 'http://www.cncaprc.gov.cn/channels/792_' + str(nextPageNum) + '.html'
            req = scrapy.Request(url=next_url, callback=self.parse)
            yield req

        for index, temp_url in enumerate(valid_child_urls):
            req = scrapy.Request(url=temp_url, callback=self.parse_info)
            m_item = YanglaoItem()
            #m_item['title'] = titles[index]
            m_item['time'] = times[index]
            m_item['className'] = '养老频道'
            req.meta['item'] = m_item
            yield req

    def parse_info(self, response):
        item = response.meta['item']

        item["source"] = "全国老龄工作委员会办公室网站"

        title_ori =  response.xpath('//div[@class="w96"]/h1/text() | //div[@class="w96"]/h1/span/text()').extract()
        title =''
        for each in title_ori:
            title = title + each
        item["title"] = title

        item["sourceUrl"] = response.url
        # 修改了text_list
        #text_list = response.xpath('//*[@id="ivs_content"]/p/text() | //*[@id="ivs_content"]/p//font/text()')
        text_list = response.xpath('//div[@class="content"]/*')
        text = processText(text_list)
        item["text"] = text

        text_list = response.xpath('//div[@class="content"]/*')
        img_list = processImgSep(text_list)
        final_img_list = []
        for img in img_list:
            if 'http' not in img:
                img = 'http://www.cncaprc.gov.cn' + img
            final_img_list.append(img)

        item['imageUrls'] = final_img_list
        if text.strip() == "" and len(img_list) == 0:
            return

        yield item
