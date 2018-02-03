# coding=utf-8
import scrapy
import re

from ..items import VideoItem


class newsSpider(scrapy.Spider):
    name = "changchenglvyou"
    start_urls = ['https://mp.weixin.qq.com/s?__biz=MzIzMTcyMzY4OA==&mid=2247485475&idx=4&sn=378527a079eac718683e29a2340dc8e5&chksm=e89e8fe4dfe906f21df3beb8ae923cd0c8433480ae74f78014738fd4b0649c39a5eb78f508ce&mpshare=1&scene=1&srcid=1202MwvAP47MhZ3kNRaXgP22&pass_ticket=ETzscQemVtZ6bwgJRRIepwgeWsLJ0TLI%2FbX7bjltdspch27wlrDnxzA5vUivZMG7#rd']

    def parse(self, response):
        section = response.xpath('//ul')[0]
        alables = section.xpath('.//a')

        titles = []
        urls = []

        for each in alables:
            url = each.xpath('@href').extract_first()
            title = each.xpath('@title').extract_first()
            if url not in urls and title is not None:
                title = title.split(" ")[-1]
                urls.append(url)
                titles.append(title)

        for title, url in zip(titles, urls):
            req = scrapy.Request(url=url, callback=self.parse_pid)
            req.meta['title'] = title
            yield req


    def parse_pid(self, response):
        title = response.meta['title']
        pid = re.findall('videoCenterId","(.*?)"', response.text)[0]
        info_url = "http://vdn.apps.cntv.cn/api/getHttpVideoInfo.do?pid=" + pid
        req = scrapy.Request(url=info_url, callback=self.parse_info)
        req.meta['sourceUrl'] = response.url
        req.meta['title'] = title
        yield req

    def parse_info(self, response):

        item = VideoItem()
        item["module"] = "兴趣爱好"
        item["className"] = "长城旅游"
        title = response.meta['title']
        if u'）' in title and title.index(u'）') != len(title)-1:
            title = title.split(u'）', 1)[1].strip(u'：')
        item["title"] = title
        urls = re.findall('jpg","url":"(.*?)"', response.text)
        #取最后的清晰度
        last_num = 1000
        for i in range(0, urls.__len__())[::-1]:
            num = int(urls[i].split('-')[-1].split('.')[0], 10)
            if num > last_num:
                item["url"] = urls[i+1:]
                break
            elif i == 0:
                item["url"] = urls
                break
            else:
                last_num = num
        item["source"] = "中国网络电视台CNTV"
        item["sourceUrl"] = response.meta['sourceUrl']
        item["poster"] = None
        item["edition"] = None

        yield item
