# coding=utf-8
import scrapy
import re

from ..items import VideoItem


class newsSpider(scrapy.Spider):
    name = "lvyou"
    start_urls = [
        'https://mp.weixin.qq.com/s?__biz=MzIzMTcyMzY4OA==&mid=2247484055&idx=6&sn=29cfb3818af2b54ebff17cf4c6ca987d&chksm=e89e8550dfe90c4636e0f136318e722073d581f2ca24f0ea8373adc75ccdefd77d682fbdcf03&mpshare=1&scene=1&srcid=12020l7fXsFMwcYZPu4ZN2ye&pass_ticket=ETzscQemVtZ6bwgJRRIepwgeWsLJ0TLI%2FbX7bjltdspch27wlrDnxzA5vUivZMG7#rd']

    def parse(self, response):
        section = response.xpath('//div[@class="rich_media_content "]/section')[1]
        alables = section.xpath('//a')

        titles = []
        urls = []

        for each in alables:
            url = each.xpath('@href').extract_first()
            title = each.xpath('strong/text()').extract_first()
            if title is not None:
                titles.append(title)
                urls.append(url)
            else:
                title = each.xpath('text()').extract_first()
                if title is not None and title[0] == u"第":
                    titles.append(title)
                    urls.append(url)


        for title, url in zip(titles,urls):
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
        item["className"] = "边疆行"
        title = response.meta['title']
        item["title"] = title.split(' ')[-1]
        item["edition"] = re.findall(u'第(.*?)集', title)[0]
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

        yield item
