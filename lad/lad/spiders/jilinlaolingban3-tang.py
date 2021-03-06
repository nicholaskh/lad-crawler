# coding=utf-8
import scrapy
import re

from ..items import YanglaoItem
from ..spiders.beautifulSoup import processText, processImgSep
from datetime import datetime
from .basespider import BaseTimeCheckSpider


class newsSpider(BaseTimeCheckSpider):
    name = "jilinlaolingban3"
    start_urls = ['http://jlllw.jl.gov.cn/llsd/index.html']

    def parse(self, response):
        should_deep = True
        times = response.xpath('//td[@valign="middle"]//td[@align="center"]/text()').extract()
        if len(times) == 0:
            should_deep = False

        # 是相对链接
        urls_ori = response.xpath('//td[@valign="middle"]//a/@href').extract()
        urls = []
        for each in urls_ori:
            if 'http://' not in each:
                url = 'http://jlllw.jl.gov.cn/llsd' + each[1:]
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

        item["source"] = "吉林省老龄工作委员会办公室网站"
        item["title"] = response.xpath('//td[@class="biaoti"]/text()').extract()[0]
        item["sourceUrl"] = response.url
        # 修改了text_list
        # text_list = response.xpath('//*[@id="ivs_content"]/p/text() | //*[@id="ivs_content"]/p//font/text()')
        text_list = response.xpath('//div[@class="TRS_Editor"]//p')
        text = processText(text_list)
        item["text"] = text

        text_list = response.xpath('//div[@class="TRS_Editor"]//p')
        img_list = processImgSep(text_list)
        final_img_list = []
        for img in img_list:
            if 'http' not in img:
                img_ori = response.url.split('/')
                image = 'http://'
                for i in range(2, len(img_ori) - 1):
                    image = image + img_ori[i] + '/'
                image = image + img[2:]
            final_img_list.append(image)

        item['imageUrls'] = final_img_list
        if text.strip() == "" and len(img_list) == 0:
            return

        yield item
