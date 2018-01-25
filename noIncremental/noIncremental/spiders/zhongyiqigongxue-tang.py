#coding=utf-8
import scrapy
from ..items import VideoItem
import re

#Code: Tom Tang
class WeChatSpider(scrapy.Spider):
    name = "zhongyiqigongxue"
    start_urls = ['https://mp.weixin.qq.com/s?__biz=MzIzMTcyMzY4OA==&mid=2247488813&idx=6&sn=8332d039056d4291fb61a830b4919f02&chksm=e89e92eadfe91bfc3a14d87688b22c89e52d74493fc71f69bea8617986227e3e144ccbcde3c1&mpshare=1&scene=1&srcid=1226r9nTsf65xVAK6D3mJlFR#rd']

    def parse(self, response):
        url_lists = response.xpath('//*[@id="js_content"]/section[3<position()]//a/@href').extract()
        for url_next in url_lists:
            if url_next.split('.')[1] == "youku":
                req = scrapy.Request(url=url_next, callback=self.youku_parseinfo)
                item = VideoItem()
                item["sourceUrl"] = url_next
                req.meta["m_item"] = item
                yield req
            elif url_next.split('.')[1] == "qq":
                req = scrapy.Request(url=url_next, callback=self.tencent_parseinfo)
                item = VideoItem()
                item["sourceUrl"] = url_next
                req.meta["m_item"] = item
                yield req

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
        item1["module"] = "舞蹈"
        item1["title"] = title
        item1["source"] = "腾讯视频"
        item1["url"] = url
        item1["poster"] = None
        item1["edition"] = None

        if u"太极剑" in title:
            item1["className"] = "太极剑教程"
        else:
            item1["className"] = "太极扇教学"

        yield item1

    def youku_parseinfo(self, response):
        page_url = response.url
        vid = page_url.split('?')[0].split('/')[-1].split('.')[0].split('_')[-1]
        url = "http://player.youku.com/embed/" + vid
        title = response.xpath('//div[@class="base_info"]/h1/@title').extract()[0]
        item1 = response.meta["m_item"]
        item1["module"] = "舞蹈"
        item1["title"] = title
        item1["source"] = "优酷视频"
        item1["url"] = url
        item1["poster"] = None
        item1["edition"] = None

        if u"中医气功学" in title:
            item1["className"] = "中医气功学"
        elif u"太极拳内功" in title:
            item1["className"] = "太极拳内功"
        elif u"理疗" in title:
            item1["className"] = "理疗瑜伽"
        elif u"每天健身" in title:
            item1["className"] = "每天健身5分钟"
        elif u"活力操" in title:
            item1["className"] = "老年活力操"
        elif u"广播体操" in title:
            item1["className"] = "广播体操"
        elif u"广场舞" in title:
            item1["className"] = "广场舞教学"
        else:
            item1["className"] = "老年锻炼操"

        yield item1