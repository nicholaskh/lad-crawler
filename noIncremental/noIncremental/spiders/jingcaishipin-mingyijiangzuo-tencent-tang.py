#coding=utf-8
import scrapy
from ..items import VideoItem
import re

#Code: Tom Tang
class WeChatSpider(scrapy.Spider):
    name = "jingcaishipin-mingyijiangzuo-tencent"
    all_class = {
        'https://v.qq.com/x/search/?ses=qid%3Dol45RnpGiqbq0O773p9qXCuhEfGDZWp3PJ86FmIKVh0t-P3XgipYoA':'洪昭光',
        'https://v.qq.com/x/search/?ses=qid%3DkCxnp7cEuScUsbEdrVzXF8pcv7Y4NloPiZFk-ASFpKIdhh6ClNRsIQ':'张悟本',
        'https://v.qq.com/x/search/?ses=qid%3D8jgWkCVnTF0M6GrjnOtsh81OCnILmfsQiwlQpeuBf5kXwVQOSI_F9Q':'陈允斌',
        'https://v.qq.com/x/search/?ses=qid%3D3lVXJ_jYyN8D3eTJylCk3tfbr1gk27ZcXKURwB8uz3P3YMuE3Hdtxg':'胡大一',
        'https://v.qq.com/x/search/?ses=qid%3DvSvggFjKzC9loyP_Mbo-AAgnDdTzMW5lO6HvffA5SJ7qnwJUpjfZCg':'路志正',
        'https://v.qq.com/x/search/?ses=qid%3DRTQLFnTuO3cbCP7pehkJWTp-x22LRDKYVaRUzudZKAJgdmEZjX7oKQ':'于康'
    }

    start_urls = ['https://v.qq.com/x/search/?ses=qid%3Dol45RnpGiqbq0O773p9qXCuhEfGDZWp3PJ86FmIKVh0t-P3XgipYoA%26last_query%3D%E6%B4%AA%E6%98%AD%E5%85%89%26tabid_list%3D0%7C7%7C15%26tabname_list%3D%E5%85%A8%E9%83%A8%7C%E5%85%B6%E4%BB%96%7C%E6%95%99%E8%82%B2&q=%E6%B4%AA%E6%98%AD%E5%85%89&stag=3&cur=1&cxt=tabid%3D0%26sort%3D0%26pubfilter%3D0%26duration%3D0',
'https://v.qq.com/x/search/?ses=qid%3DkCxnp7cEuScUsbEdrVzXF8pcv7Y4NloPiZFk-ASFpKIdhh6ClNRsIQ%26last_query%3D%E5%BC%A0%E6%82%9F%E6%9C%AC%26tabid_list%3D0%7C7%7C3%7C11%7C13%26tabname_list%3D%E5%85%A8%E9%83%A8%7C%E5%85%B6%E4%BB%96%7C%E7%BB%BC%E8%89%BA%7C%E6%96%B0%E9%97%BB%7C%E8%B4%A2%E7%BB%8F&q=%E5%BC%A0%E6%82%9F%E6%9C%AC&stag=3&cur=1&cxt=tabid%3D0%26sort%3D0%26pubfilter%3D0%26duration%3D0',
'https://v.qq.com/x/search/?ses=qid%3D8jgWkCVnTF0M6GrjnOtsh81OCnILmfsQiwlQpeuBf5kXwVQOSI_F9Q%26last_query%3D%E9%99%88%E5%85%81%E6%96%8C%26tabid_list%3D0%7C7%7C3%7C11%7C8%26tabname_list%3D%E5%85%A8%E9%83%A8%7C%E5%85%B6%E4%BB%96%7C%E7%BB%BC%E8%89%BA%7C%E6%96%B0%E9%97%BB%7C%E5%8E%9F%E5%88%9B&q=%E9%99%88%E5%85%81%E6%96%8C&stag=3&cur=1&cxt=tabid%3D0%26sort%3D0%26pubfilter%3D0%26duration%3D0',
'https://v.qq.com/x/search/?ses=qid%3D3lVXJ_jYyN8D3eTJylCk3tfbr1gk27ZcXKURwB8uz3P3YMuE3Hdtxg%26last_query%3D%E8%83%A1%E5%A4%A7%E4%B8%80%26tabid_list%3D0%7C11%7C7%26tabname_list%3D%E5%85%A8%E9%83%A8%7C%E6%96%B0%E9%97%BB%7C%E5%85%B6%E4%BB%96&q=%E8%83%A1%E5%A4%A7%E4%B8%80&stag=3&cur=1&cxt=tabid%3D0%26sort%3D0%26pubfilter%3D0%26duration%3D0',
'https://v.qq.com/x/search/?ses=qid%3DvSvggFjKzC9loyP_Mbo-AAgnDdTzMW5lO6HvffA5SJ7qnwJUpjfZCg%26last_query%3D%E8%B7%AF%E5%BF%97%E6%AD%A3%26tabid_list%3D0%7C7%26tabname_list%3D%E5%85%A8%E9%83%A8%7C%E5%85%B6%E4%BB%96&q=%E8%B7%AF%E5%BF%97%E6%AD%A3&stag=3&cur=1&cxt=tabid%3D0%26sort%3D0%26pubfilter%3D0%26duration%3D0',
'https://v.qq.com/x/search/?ses=qid%3DRTQLFnTuO3cbCP7pehkJWTp-x22LRDKYVaRUzudZKAJgdmEZjX7oKQ%26last_query%3D%E4%BA%8E%E5%BA%B7%26tabid_list%3D0%7C7%7C3%7C1%7C11%7C15%26tabname_list%3D%E5%85%A8%E9%83%A8%7C%E5%85%B6%E4%BB%96%7C%E7%BB%BC%E8%89%BA%7C%E7%94%B5%E5%BD%B1%7C%E6%96%B0%E9%97%BB%7C%E6%95%99%E8%82%B2&q=%E4%BA%8E%E5%BA%B7&stag=3&cur=1&cxt=tabid%3D0%26sort%3D0%26pubfilter%3D0%26duration%3D0'
]

    def parse(self, response):
        url_ori = response.xpath('/html/body/div[2]/div[2]/div[1]//a/@href').extract()
        url_lists = list(set(url_ori))

        for url_next in url_lists:
            if '/x/page' in url_next:
                req = scrapy.Request(url=url_next, callback=self.tencent_parseinfo)
                item = VideoItem()
                item["sourceUrl"] = url_next
                item['className'] = self.all_class[response.url[:91]]
                req.meta["m_item"] = item
                yield req

        nextPage_ori = response.url.split('&')
        nextPage = ''
        for each in nextPage_ori:
            if each[:-1] == 'cur=':
                currentPage = int(each.split('=')[-1])
                nextPageNum = currentPage + 1
                nextPage = nextPage + 'cur=' + str(nextPageNum) + '&'
            else:
                nextPage = nextPage + each + '&'
        req_next = scrapy.Request(url=nextPage[:-1], callback=self.parse)
        yield req_next

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
        if len(title) == 0:
            return

        item1["module"] = "名医讲座"
        item1["title"] = title
        item1["source"] = "腾讯视频"
        item1["url"] = url
        item1["poster"] = None
        item1["edition"] = None

        yield item1
