# coding=utf-8
import scrapy
import re

from ..items import VideoItem


class newsSpider(scrapy.Spider):
    name = "yangshengtang"
    start_urls = ['https://mp.weixin.qq.com/s?__biz=MzIzMTcyMzY4OA==&mid=2247483699&idx=1&sn=f59acb95f4fe98df5e401c38f415c2b7&chksm=e89e86f4dfe90fe20476036da52f85804611ee1e83c639bff69717aa08c087adf71c9ddd6984&mpshare=1&scene=1&srcid=12020cFXG3GOAAJTpPxwwGyI&pass_ticket=ETzscQemVtZ6bwgJRRIepwgeWsLJ0TLI%2FbX7bjltdspch27wlrDnxzA5vUivZMG7#rd']

    def parse(self, response):
        alabels = response.xpath('//div[@class="rich_media_content "]/p/a')

        titles = []
        vids = []

        for each in alabels:
            url = each.xpath('@href').extract_first()
            title = each.xpath('text()').extract_first()
            vid_list = re.findall('id_(.*?).html', url)
            #vid_list 和 title不空
            if vid_list and title is not None:
                vid =vid_list[0]
                if vid not in vids:
                    vids.append(vid)
                    titles.append(title)
                elif title not in titles:
                    titles[vids.index(vid)] = titles[vids.index(vid)] + title

        for title, vid in zip(titles, vids):
            item = VideoItem()
            item["module"] = "营养课堂"
            item['className'] = "养生堂"
            item["title"] = title
            item["url"] = "http://player.youku.com/embed/" + vid
            item["source"] = "优酷视频"
            item["sourceUrl"] = "http://v.youku.com/v_show/id_" + vid + ".html"
            item["poster"] = None
            item["edition"] = None
            yield item



    # def parse(self, response):
    #     hrefs = response.xpath('//div[@class="rich_media_content "]/p/a/@href').extract()
    #
    #     urls = []
    #     for url in hrefs:
    #         if "v.youku" in url and url not in urls:
    #             urls.append(url)
    #             req = scrapy.Request(url=url, callback=self.parse_youku)
    #             yield req
    #
    # def parse_youku(self, response):
    #     item = VideoItem()
    #     item["module"] = "营养课堂"
    #     title = response.xpath('//h1[@class="title"]/@title')
    #     item['className'] = "养生堂"
    #     if title:
    #         item["title"] = title.extract_first()
    #     else:
    #         title = response.xpath('//*[@id="subtitle"]/@title').extract_first()
    #         if title is not None:
    #             item["edition"] = title.rsplit(' ', 1)[1]
    #             item["title"] = title.rsplit(' ', 1)[0]
    #         else:
    #
    #     item["source"] = "优酷视频"
    #     item["sourceUrl"] = response.url
    #     item["url"] = "http://player.youku.com/embed/" + re.findall('id_(.*?).html', response.url)[0]
    #
    #     yield item


