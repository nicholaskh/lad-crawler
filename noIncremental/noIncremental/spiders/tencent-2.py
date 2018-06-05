#coding=utf-8
import scrapy
from ..items import VideoItem
import re

#Code: Tom Tang
class WeChatSpider(scrapy.Spider):
    name = 'tencent-2'
    start_dicts = {'http://v.qq.com/detail/x/x83ipjk9n4qgj1m.html':'宝宝健康食谱',
                   'http://v.qq.com/detail/0/02twwtze22guq9g.html':'健康餐食谱',
                   'http://v.qq.com/detail/j/j99nmu913n28m44.html':'宴客食谱',
                   'http://v.qq.com/detail/q/q70zj0gepiz2hs0.html':'早餐食谱',
                   'http://v.qq.com/detail/f/fala751mofpdld2.html':'汤水食谱',
                   'http://v.qq.com/detail/f/fj1mzp9147oh3fx.html':'学龄前儿童食谱'}
    start_urls = list(start_dicts.keys())

    def parse(self, response):
        id = response.url.split('/')[-1].split('.')[0]
        range = response.xpath('//span[@class="_tabsNav"]/a/text()').extract()[0].split('-')[-1]
        dataUrl = 'http://s.video.qq.com/get_playsource?id=' + id + '&type=4&range=1-' + range + '&otype=json'
        req = scrapy.Request(url=dataUrl, callback=self.tencent_parseDataInfo)
        item = VideoItem()
        item["module"] = "健康食谱"
        item["className"] = self.start_dicts[response.url]
        req.meta["mm_item"] = item
        yield req

    def tencent_parseDataInfo(self, response):
        urls = re.findall(r'"playUrl":"(.*?)"',response.text)
        for eachUrl in urls:
            item11 = response.meta["mm_item"]
            req = scrapy.Request(eachUrl, callback=self.tencent_parseinfo)
            req.meta["m_item"] = item11
            yield req

    def tencent_parseinfo(self, response):
        page_url = response.url
        vid = response.url.split('=')[-1]
        url = "https://v.qq.com/iframe/player.html?vid=" + vid + "&tiny=0&auto=0"
        title_ori = response.xpath('//div[@class="mod_intro"]/div/h1/text()').extract()[0]
        title = ""
        for i in range(len(title_ori)):
            if title_ori[i] != '\n':
                if title_ori[i] != ' ':
                    if title_ori[i] != '\t':
                        title = title +title_ori[i]

        item1 = response.meta["m_item"]
        item1["title"] = title
        item1["source"] = "腾讯视频"
        item1["url"] = url
        item1["poster"] = None
        item1["edition"] = None
        item1["sourceUrl"] = response.url

        yield item1