# coding=utf-8
import scrapy
import re

from ..items import VideoItem


class newsSpider(scrapy.Spider):
    name = "xuesuona"
    start_urls = ['https://mp.weixin.qq.com/s/cS7EYEIel-Iz_LtT7TTFOg']

    def parse(self, response):
        urls_1 = response.xpath('//section[@style="color: rgb(249, 110, 87);box-sizing: border-box;"]/h2/span/a/@href').extract()
        titles_1 = response.xpath('//section[@style="color: rgb(249, 110, 87);box-sizing: border-box;"]/h2/span/a/text()').extract()
        urls_2 = response.xpath('//section[@style="color: rgb(249, 110, 87);box-sizing: border-box;"]/h2/a/@href').extract()
        del urls_2[0]
        titles_2 = response.xpath('//section[@style="color: rgb(249, 110, 87);box-sizing: border-box;"]/h2/a/span/text()').extract()
        urls = urls_1 + urls_2
        titles = titles_1 + titles_2
        del urls[3]
        del titles[3]

        for title, url in zip(titles, urls):
            req = scrapy.Request(url=url, callback=self.parse_url)
            req.meta['title'] = title
            yield req

    def parse_url(self, response):
        item = VideoItem()
        item["module"] = "兴趣爱好"
        item['className'] = "学唢呐"
        item["title"] = response.meta['title']
        url = response.xpath('//*[@id="icontent"]/div/div[2]/iframe/@src').extract_first()
        if url is not None:
            vid = url.split('/')[-1]
            item["url"] = url
        else:
            url_2 = response.xpath('//param[@name="movie"]/@value').extract_first()
            vid = url_2.split('/')[-2]
            item["url"] = "http://player.youku.com/embed/" + vid
        item["source"] = "优酷视频"
        item["sourceUrl"] = "http://v.youku.com/v_show/id_" + vid + ".html"
        item["poster"] = None
        item["edition"] = None
        yield item
