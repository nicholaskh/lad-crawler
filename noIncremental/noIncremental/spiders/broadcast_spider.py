#coding=utf-8
import scrapy

from ..items import BroadcastItem
from scrapy.conf import settings
from noIncremental.spiders.beautifulSoup import processText
import requests
import json
import re
import random

class NewsSpider(scrapy.Spider):

    name = "broadtest"
    districts = [
'5286989/album/4336951',
'85559503/album/10388270',
'85559503/album/10388270',
'5286989/album/4336951',
'63246511/album/5734107',
'57476658/album/5243276',
'3488043/album/2968683',
'54422955/album/6394073',
'32818259/album/2986176',
'26358409/album/410276',
'71166303/album/6611301',
'7816526/album/246264',
'75948693/album/7053033',
'27735013/album/6143009',
'33178188/album/7368338',
'66526203/album/6495091',
'53548518/album/8013915',
'27735013/album/3809485',
'5286989/album/10114187',
'66504855/album/6070605',
'81274819/album/9168442',
'67724162/album/7491792',
'51359628/album/5546248',
'48511482/album/5623398',
'44323468/album/6535714',
'20606834/album/326664',
'46141065/album/5336043',
'42038474/album/4220332',
'29564424/album/2735915',
'85095510/album/10084276',
'55454651/album/6715305',
'81274819/album/8164396',
'34759447/album/5196918',
'87015138/album/10165651',
'63011749/album/5964619',
'59171436/album/6689571',
'35413984/album/3260016',
'36341230/album/3848122',
'26702353/album/414916',
'25574497/album/6680934',
'24595769/album/4526785',
'36190798/album/6509727',
'18565048/album/8773943',
'41727503/album/3671731',
'8288167/album/264908',
'43646998/album/4822564',
'36831660/album/5625092',
'74081976/album/6762275',
'46573369/album/6937155',
'18692594/album/304667',
'69824839/album/9818710',
'14758971/album/281147',
'43550896/album/5454422',
'85359362/album/9049929',
'12376368/album/276104',
'32636937/album/3192536',
'32818259/album/10179568',
'67170948/album/6936488',
'36463023/album/7824770',
'69255024/album/6294450',
'87860640/album/9582563',
'44764942/album/3946441',
'58761970/album/6858374',
'77062670/album/7283068',
'51740814/album/6035138',
'20283508/album/9410827',
'32311640/album/6142190',
'52752925/album/5491269',
'1841872/album/373712',
'27735013/album/4244741',
'72915361/album/6676223',
'20983343/album/351738',
'85095510/album/8704197',
'55952101/album/7751418',
'29564424/album/3021211',
'27020530/album/469933',
'57947833/album/5799814',
'38502824/album/4528480',
'63252997/album/5713905',
'59171436/album/6162503',
'29784782/album/2840643',
'14913400/album/3515153',
'81274819/album/9168462',
'25418876/album/4701702',
'29564424/album/3023007',
'3727870/album/214541',
'29547135/album/7151385',
'55454651/album/6797679',
'64079749/album/9728850',
'60506402/album/5444508',
'59171436/album/6843092',
'69164821/album/6967386',
'51429761/album/4727556',
'63900952/album/5765890',
'88689964/album/9889288',
'18762711/album/3911030',
'41547583/album/6976818',
'53706710/album/4632668',
'53548518/album/7607172',
'56946622/album/4981202',
'85562053/album/8805834',
'28203563/album/3230524',
'69255024/album/6454374',
'29564424/album/3023265',
'82360020/album/8564098',
'38451690/album/4592294',
'61332164/album/5502184',
'39965511/album/9479059',
'24376408/album/378827',
'45577023/album/6854668',
'61332164/album/5733899',
'81942493/album/9616758',
'47118564/album/10144041',
'69164821/album/6688891',
'42776592/album/6457863',
'53096499/album/4566129',
'52752925/album/4565201',
'35266642/album/5936222',
'88205133/album/10296231',
'67331429/album/7307239',
'78610474/album/9106756',
'63051686/album/9329397',
'12457600/album/9988420',
'68729923/album/9825356',
'27735013/album/3935093',
'31981120/album/7952892',
'19003844/album/5078968',
'38953361/album/3413625',
'74273974/album/7760217',
'64122282/album/8853033',
'25271822/album/2754544'
]
    start_urls = ['http://www.ximalaya.com/%s/' % x for x in districts]

    def parse(self, response):

        if len(response.xpath('//*[@class="pagingBar_wrapper"]/a')) > 0:
            if response.xpath('//*[@class="pagingBar_wrapper"]/a')[-1].xpath('@href').extract_first() is not None:
                if response.xpath('//*[@class="pagingBar_wrapper"]/a/text()')[-1].extract().encode('utf-8') == '下一页':
                    next_page_url = 'http://www.ximalaya.com' + response.xpath('//*[@class="pagingBar_wrapper"]/a')[-1].xpath('@href').extract_first()
                    yield scrapy.Request(url=next_page_url, callback=self.parse)

        for infoDiv in response.xpath('//*[@class="title"]/@href').extract():
            n_url = "http://www.ximalaya.com" + infoDiv
            req = scrapy.Request(url=n_url, callback=self.parse_info)
            m_item = BroadcastItem()
            m_item['className'] = response.xpath('//*[@class="detailContent_title"]/h1/text()').extract_first()
            req.meta['item'] = m_item
            yield req
    def parse_info(self, response):

        headers1 = {
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Encoding': 'gzip, deflate, sdch',
            'Accept-Language': 'zh-CN,zh;q=0.8,en;q=0.6',
            'Cache-Control': 'max-age=0',
            'Proxy-Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1',
            'User-Agent': random.choice(settings["USER_AGENTS"])
        }

        item = response.meta['item']

        item["module"] = "健康养生"
        item["title"] = response.xpath('//*[@class="detailContent_title"]/h1/text()').extract_first()
        try:
            item["edition"] = re.findall(r"\d+\d*",response.xpath('//*[@class="detailContent_title"]/h1/text()').extract_first())[0]
        except:
            print "no edition"
            item["edition"] = None
        item["source"] = "喜马拉雅FM"
        item["sourceUrl"] = response.url
        item["intro"] = ''
        if len(response.xpath('//*[@class="mid_intro"]/article/a/text()')) != 0:
            item["intro"] = response.xpath('//*[@class="mid_intro"]/article/a/text()').extract_first().strip()
        if len(response.xpath('//*[@class="mid_intro"]/article/text()')) != 0:
            item["intro"] = response.xpath('//*[@class="mid_intro"]/article/text()').extract_first().strip()
        id_number = response.url.split('/')[-2]
        murl = 'http://www.ximalaya.com/tracks/' + id_number + '.json'
        html = requests.get(murl, headers=headers1).text
        item["broadcast_url"] = json.loads(html)["play_path"]

        yield item
