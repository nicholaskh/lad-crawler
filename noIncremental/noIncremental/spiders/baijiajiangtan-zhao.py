# coding=utf-8
import scrapy
import re

from ..items import VideoItem


class newsSpider(scrapy.Spider):
    name = "baijiajiangtan"
    start_urls = ['https://mp.weixin.qq.com/s?__biz=MzIzMTcyMzY4OA==&mid=2247486048&idx=2&sn=a0279cf67b9d02cd412a686b7b284a50&chksm=e89e8da7dfe904b1d6ae5d34fab5bea2dace32459d88bf96cc3f4dfd763b4cc57e2b5863eb5b&mpshare=1&scene=1&srcid=12025SZImrPSz5PmUtup9vmd&pass_ticket=ETzscQemVtZ6bwgJRRIepwgeWsLJ0TLI%2FbX7bjltdspch27wlrDnxzA5vUivZMG7#rd']

    def parse(self, response):
        section = response.xpath('//section[@style="display: inline-table; border-collapse: collapse; table-layout: fixed; width: 100%; box-sizing: border-box;"]')
        hrefs = section.xpath('.//a/@href').extract()

        #turn to every sub collection page
        #h2 格式的
        h2_url = hrefs[-1]
        req = scrapy.Request(url=h2_url, callback=self.parse_h2)
        yield req
        del hrefs[-1]
        #ul 格式的
        for url in hrefs:
            req = scrapy.Request(url=url, callback=self.parse_ul)
            yield req

    def parse_ul(self, response):
        uls = response.xpath('//ul')
        titles = []
        hrefs = []
        #ul 格式的提取
        for ul in uls:
            alabels = ul.xpath('.//a')
            for each in alabels:
                title = each.xpath('@title').extract_first()
                href = each.xpath('@href').extract_first()
                if title is not None and title not in titles and href not in hrefs:
                    titles.append(title)
                    hrefs.append(href)

        for href, title in zip(hrefs, titles):
            if "youku" in href:
                vid = re.findall('id_(.*?).html', href)[0]
                item = VideoItem()
                item["module"] = "教育法律"
                item["className"] = "百家讲坛"
                item["title"] = title
                item["url"] = "http://player.youku.com/embed/" + vid
                item["source"] = "优酷视频"
                item["sourceUrl"] = href
                item["poster"] = None
                item["edition"] = None
                yield item
            elif "qq" in href:
                vid = href.split("/")[-1].split(".")[0]
                item = VideoItem()
                item["module"] = "教育法律"
                item["className"] = "百家讲坛"
                item["title"] = title
                item["url"] = "https://v.qq.com/iframe/player.html?vid=" + vid + "&tiny=0&auto=0"
                item["source"] = "腾讯视频"
                item["sourceUrl"] = href
                item["poster"] = None
                item["edition"] = None
                yield item
            elif "cntv" in href:
                req = scrapy.Request(url=href, callback=self.parse_pid)
                req.meta['title'] = title
                yield req


    def parse_h2(self, response):
        h2s = response.xpath('//h2')
        titles = []
        hrefs = []
        # h2 格式的提取
        for h2 in h2s:
            alabels = h2.xpath('.//a')
            for each in alabels:
                title = ""
                href = each.xpath('@href').extract_first()
                strong = each.xpath('strong/text()')
                if strong:
                    title = title + strong.extract_first()
                else:
                    title = title + each.xpath('text()').extract_first()
                if title != "" and title not in titles and href not in hrefs:
                    titles.append(title)
                    hrefs.append(href)

        for href, title in zip(hrefs, titles):
            if "youku" in href:
                vid = re.findall('id_(.*?).html', href)[0]
                item = VideoItem()
                item["module"] = "教育法律"
                item["className"] = "百家讲坛"
                item["title"] = title
                item["url"] = "http://player.youku.com/embed/" + vid
                item["source"] = "优酷视频"
                item["sourceUrl"] = href
                item["poster"] = None
                item["edition"] = None
                yield item
            elif "qq" in href:
                vid = href.split("/")[-1].split(".")[0]
                item = VideoItem()
                item["module"] = "教育法律"
                item["className"] = "百家讲坛"
                item["title"] = title
                item["url"] = "https://v.qq.com/iframe/player.html?vid=" + vid + "&tiny=0&auto=0"
                item["source"] = "腾讯视频"
                item["sourceUrl"] = href
                item["poster"] = None
                item["edition"] = None
                yield item
            elif "cntv" in href:
                req = scrapy.Request(url=href, callback=self.parse_pid)
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
        item["module"] = "教育法律"
        item["className"] = "百家讲坛"
        item["title"] = response.meta['title']
        urls = re.findall('jpg","url":"(.*?)"', response.text)
        # 取最后的清晰度
        last_num = 1000
        for i in range(0, urls.__len__())[::-1]:
            num = int(urls[i].split('-')[-1].split('.')[0], 10)
            if num > last_num:
                item["url"] = urls[i + 1:]
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
