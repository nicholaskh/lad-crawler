#coding=utf-8
import scrapy
import re

from ..items import LadItem
from ..spiders.beautifulSoup import processText, processImgSep
from datetime import datetime
from .basespider import BaseTimeCheckSpider

class newsSpider(BaseTimeCheckSpider):
    name = "hebeigongan"
    start_urls = ['http://www.hebga.gov.cn/default.php?mod=article&settype=0&fid=242&s15801039_start=0']

    def parse(self, response):
        should_deep = True
        times_ori = response.xpath('//*[@id="s15801039_content"]/table/tbody//tr/td/span[2]/text()').extract()
        times = []
        for each in times_ori:
            time = each[3:-1]
            times.append(time)

        #是相对链接
        urls_ori = response.xpath('//*[@id="s15801039_content"]/table/tbody//a/@href').extract()
        urls = []
        for each in urls_ori:
            if 'start' not in each:
                url = 'http://www.hebga.gov.cn/' + each
                urls.append(url)

        #titles = response.xpath('/html/body/div[3]/div/div/div/div[3]/div/table/tbody//a/text()').extract()

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
            currentPageNum = int(response.url.split('=')[-1])
            temp = response.xpath('//*[@id="s15801039_content"]/table/tbody//a/text()').extract()
            continuetocrawl = False
            if u'下一页' in temp:
                continuetocrawl = True

            if continuetocrawl == True:
                nextPageNum = currentPageNum + 18
                next_url = 'http://www.hebga.gov.cn/default.php?mod=article&settype=0&fid=242&s15801039_start=' + str(nextPageNum)
                req = scrapy.Request(url=next_url, callback=self.parse)
                yield req

        for index, temp_url in enumerate(valid_child_urls):
            req = scrapy.Request(url=temp_url, callback=self.parse_info)
            m_item = LadItem()
            m_item['time'] = times[index]
            #m_item['title'] = titles[index]
            m_item['newsType'] = "警事要闻"
            req.meta['item'] = m_item
            yield req

    def parse_info(self, response):
        item = response.meta['item']

        item["city"] = "河北公安网"
        #item["title"] = response.xpath('//dt[@class="f_22 fc_2d"]/text()').extract()[0].strip()
        item["title"] = response.xpath('//*[@id="s3636946_content"]/div/table[1]/tbody/tr[1]/td/text()').extract()[0]
        item["sourceUrl"] = response.url
        # 修改了text_list
        #text_list = response.xpath('//*[@id="ivs_content"]/p/text() | //*[@id="ivs_content"]/p//font/text()')
        text_list = response.xpath('//font[@color="#333333"]/*')
        text = processText(text_list)
        item["text"] = text

        text_list = response.xpath('//font[@color="#333333"]/*')
        img_list = processImgSep(text_list)
        final_img_list = []
        for img in img_list:
            if 'http' not in img:
                img = 'http://www.hebga.gov.cn' + img
            final_img_list.append(img)
        item['imageUrls'] = final_img_list
        if text.strip() == "" and len(img_list) == 0:
            return

        yield item
