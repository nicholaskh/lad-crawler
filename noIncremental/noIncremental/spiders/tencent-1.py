#coding=utf-8
import scrapy
from ..items import VideoItem
import re

#Code: Tom Tang
class WeChatSpider(scrapy.Spider):
    name = "tencent-1"
    start_urls = ['https://v.qq.com/x/search/?q=%E4%BD%9B%E6%95%99%E9%9F%B3%E4%B9%90&stag=0&ses=qid%3DJCBhDNB9OYqLizbVTUfzNMtrKXLkEMDcYbKCM3KZdAjNzfbY_d-NlQ%26last_query%3D%E8%88%9E%E8%B9%88%26tabid_list%3D0%7C7%7C8%7C5%7C4%7C15%7C1%7C3%7C12%7C20%26tabname_list%3D%E5%85%A8%E9%83%A8%7C%E5%85%B6%E4%BB%96%7C%E5%8E%9F%E5%88%9B%7C%E9%9F%B3%E4%B9%90%7C%E5%8A%A8%E6%BC%AB%7C%E6%95%99%E8%82%B2%7C%E7%94%B5%E5%BD%B1%7C%E7%BB%BC%E8%89%BA%7C%E5%A8%B1%E4%B9%90%7C%E6%AF%8D%E5%A9%B4']

    def parse(self, response):
        url_lists = response.xpath('//div[@class="wrapper_main"]//div[@class="result_item result_item_h _quickopen"]/h2/a/@href').extract()
        for url_next in url_lists:
            if url_next.split('.')[1] == "qq":
                req = scrapy.Request(url=url_next, callback=self.tencent_parseinfo)
                item = VideoItem()
                item["sourceUrl"] = url_next
                req.meta["m_item"] = item
                yield req

        currentPage = int(response.url.split('&')[-2].split('=')[-1])
        nextPage = currentPage + 1
        if nextPage < 10:
            nextUrl = 'https://v.qq.com/x/search/?ses=qid%3DNx1_gIQgKj00G1VHO8pnfyjGzF0SiTRXqVYWA9Vw1LDXWu6PSQXsAg%26last_query%3D%E4%BD%9B%E6%95%99%E9%9F%B3%E4%B9%90%26tabid_list%3D0%7C7%7C5%7C8%7C15%7C2%7C1%7C3%7C6%7C12%26tabname_list%3D%E5%85%A8%E9%83%A8%7C%E5%85%B6%E4%BB%96%7C%E9%9F%B3%E4%B9%90%7C%E5%8E%9F%E5%88%9B%7C%E6%95%99%E8%82%B2%7C%E7%94%B5%E8%A7%86%E5%89%A7%7C%E7%94%B5%E5%BD%B1%7C%E7%BB%BC%E8%89%BA%7C%E7%BA%AA%E5%BD%95%E7%89%87%7C%E5%A8%B1%E4%B9%90&q=%E4%BD%9B%E6%95%99%E9%9F%B3%E4%B9%90&stag=3&cur=' + str(
            nextPage) + '&cxt=tabid%3D0%26sort%3D0%26pubfilter%3D0%26duration%3D0'
            req_nextPage = scrapy.Request(url=nextUrl, callback=self.parse)
            yield req_nextPage

    def tencent_parseinfo(self, response):
        page_url = response.url
        vid = page_url.split('/')[-1].split('.')[0]
        url = "https://v.qq.com/iframe/player.html?vid=" + vid + "&tiny=0&auto=0"
        title_ori = response.xpath('//div[@class="mod_intro"]/div/h1/text()').extract()[0]
        title = ""
        for i in range(len(title_ori)):
            if title_ori[i] != '\n':
                if title_ori[i] != ' ':
                    if title_ori[i] != '\t':
                        title = title +title_ori[i]

        item1 = response.meta["m_item"]
        item1["module"] = "佛教音乐"
        item1["title"] = title
        item1["source"] = "腾讯视频"
        item1["url"] = url
        item1["poster"] = None
        item1["edition"] = None
        item1["className"] = "佛教音乐"

        yield item1
