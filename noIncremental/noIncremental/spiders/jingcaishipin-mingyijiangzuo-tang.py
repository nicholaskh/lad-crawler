#coding=utf-8
import scrapy
from ..items import VideoItem
import re

#Code: Tom Tang
class WeChatSpider(scrapy.Spider):
    name = 'jingcaishipin-mingyijiangzuo'
    start_urls = ['http://www.iqiyi.com/a_19rrhal6q9.html',
                  'http://www.iqiyi.com/a_19rrh8gf71.html',
'http://www.iqiyi.com/a_19rrh8gnsd.html',
'http://www.iqiyi.com/a_19rrh8gd2l.html',
'http://www.iqiyi.com/a_19rrh8hlzx.html',
'http://www.iqiyi.com/a_19rrh7swgl.html',
'http://www.iqiyi.com/a_19rrh8t5t9.html',
'http://www.iqiyi.com/a_19rrh8gfj1.html',
'http://www.iqiyi.com/a_19rrh8gnyt.html',
'http://www.iqiyi.com/a_19rrh7a4ad.html',
'http://www.iqiyi.com/a_19rrh8jy39.html',
'http://www.iqiyi.com/a_19rrhdkbyt.html',
'http://www.iqiyi.com/a_19rrh8jkud.html',
'http://www.iqiyi.com/a_19rrh78gj9.html',
'http://www.iqiyi.com/a_19rrhc7dc5.html',
'http://www.iqiyi.com/a_19rrhbzrjx.html',
'http://www.iqiyi.com/a_19rrhb0l6l.html',
'http://www.iqiyi.com/a_19rrhafs8d.html',
'http://www.iqiyi.com/a_19rrhb0lax.html',
'http://www.iqiyi.com/a_19rrhb0v1x.html',
'http://www.iqiyi.com/a_19rrhb8e1d.html',
'http://www.iqiyi.com/a_19rrhbevo1.html',
'http://www.iqiyi.com/a_19rrhb0lx5.html',
'http://www.iqiyi.com/a_19rrhb0jdx.html',
'http://www.iqiyi.com/a_19rrha90u5.html',
'http://www.iqiyi.com/a_19rrhb8fd9.html',
'http://www.iqiyi.com/a_19rrhb9fe1.html',
'http://www.iqiyi.com/a_19rrhb0vex.html',
'http://www.iqiyi.com/a_19rrhb0m6p.html',
'http://www.iqiyi.com/a_19rrhb0nuh.html',
'http://www.iqiyi.com/a_19rrhb0m09.html',
'http://www.iqiyi.com/a_19rrhb0nox.html']

    def parse(self, response):
        url_ori = response.xpath('//*[@id="albumpic-showall-wrap"]//a/@href').extract()
        url_lists = list(set(url_ori))
        for url_next in url_lists:
            req = scrapy.Request(url=url_next, callback=self.iqiyi_parseinfo)
            item = VideoItem()
            item["sourceUrl"] = url_next
            req.meta["m_item"] = item

            className_ori = response.xpath('//*[@id="block-D"]/div/div/div[2]/div/h1/a/text()').extract()[0]
            if u'【尚医健康】' in className_ori:
                item['className'] = className_ori.split(u'】')[-1]
            else:
                item['className'] = className_ori

            yield req

    def iqiyi_parseinfo(self, response):
        vid = str(re.findall(r'data-player-videoid="(.*?)"', response.text)[0])
        tvld = str(re.findall(r'tvId:(.*?),',response.text)[0])
        url = "http://open.iqiyi.com/developer/player_js/coopPlayerIndex.html?vid=" + vid + "&tvId=" + tvld
        title = response.xpath('//*[@id="widget-videotitle"]/text()').extract()[0][1:]

        item1 = response.meta["m_item"]
        item1["module"] = "名医讲座"
        #item1["className"] = "吴林-心内科"
        item1["title"] = title
        item1["source"] = "爱奇艺"
        item1["url"] = url
        item1["edition"] = None
        item1["poster"] = None

        # className_ori = response.xpath('//*[@id="block-D"]/div/div/div[2]/div/h1/a/text()').extract()[0]
        # if u'【尚医健康】' in className_ori:
        #     item1['className'] = className_ori.split(u'】')[-1]
        # else:
        #     item1['className'] = className_ori

        yield item1