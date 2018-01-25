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

    name = "broadtest2"
    districts = [
'51657646/album/5330589',
'7473169/album/301969',
'65951140/album/6058561',
'38698704/album/6161628',
'53780147/album/4852798',
'68729923/album/10579365',
'31881074/album/2866183',
'41969594/album/4036894',
'26167595/album/7237256',
'22176892/album/4071788',
'69213053/album/7725227',
'41545555/album/3946692',
'19003844/album/323305',
'7816526/album/3262949',
'79838065/album/8424992',
'31963992/album/5435922',
'22210416/album/468981',
'55332991/album/7949620',
'78673877/album/9556975',
'21606525/album/6222968',
'37655329/album/6605727',
'8785237/album/259734',
'53181958/album/7950826',
'25817621/album/5489556',
'75181679/album/7181620',
'33178188/album/8241446',
'82457372/album/8696514',
'45819056/album/4788557',
'77841448/album/7478196',
'53991279/album/5390855',
'59189347/album/6364105',
'30302080/album/7876219',
'26032100/album/3554972',
'37561485/album/3410196',
'58785305/album/8283528',
'79753113/album/7823370',
'22374879/album/6067671',
'60248807/album/9009282',
'81795533/album/10377905',
'61092274/album/5481428',
'28539227/album/4548395',
'41399887/album/5110544',
'52076721/album/4530550',
'46232245/album/5130637',
'19003844/album/319844',
'43646998/album/4147608',
'42378914/album/5166324',
'27941321/album/2848971',
'33921593/album/6363910',
'54071606/album/9572190',
'43834795/album/4867487',
'34106176/album/4368650',
'2380669/album/5966314',
'34309363/album/7606750',
'2420751/album/3156763',
'63051686/album/5676427',
'14985561/album/289915',
'34488266/album/3034851',
'91788340/album/10366241',
'85132992/album/8734808',
'19641209/album/9459494',
'30231868/album/4020035',
'54138558/album/4800318',
'44157486/album/4924688',
'66311272/album/9916910',
'38502824/album/5342849',
'1438008/album/191438',
'37655329/album/6961481',
'45819056/album/7270661',
'81227563/album/8418663',
'81352324/album/8154812',
'30232871/album/7904098',
'1000566/album/960',
'79686700/album/7808763',
'20615173/album/3404852',
'29391163/album/3941334',
'48222317/album/4327973',
'12475246/album/2881938',
'19003844/album/4898079',
'26702353/album/425674',
'71985720/album/9618552',
'42614795/album/7521565',
'57501781/album/5079953',
'78445410/album/9694971',
'41810193/album/8166484',
'53290788/album/4930587',
'15461250/album/4626815',
'77027426/album/7633702',
'28666480/album/5849952',
'53484301/album/5253361',
'56457069/album/9481960',
'61332164/album/5625390',
'51266740/album/4448364',
'37655329/album/6961436',
'28219958/album/9349956',
'20606834/album/3175222',
'25504353/album/3594941',
'51657646/album/5582853',
'44638326/album/4483141',
'57130352/album/4987153',
'76581655/album/7842050',
'59624985/album/5290067',
'52752925/album/4570317',
'18234526/album/2731216',
'46232245/album/4901851',
'53552512/album/4617353',
'38502824/album/3860387',
'26167595/album/8649469',
'73987141/album/8913532',
'76412126/album/7543861',
'34493560/album/4387262',
'38876036/album/5566622',
'48582473/album/7523876',
'70207107/album/9799277',
'45938347/album/4022100',
'43646998/album/4193315',
'22129256/album/1072869',
'78569797/album/9346262',
'43476323/album/3887292',
'34493560/album/4235563',
'71166303/album/9942211',
'27231979/album/2762436',
'59064983/album/5580315',
'44841033/album/3881168',
'2452186/album/3680447'
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
        # item["play_times"] = response.xpath('//*[@class="soundContent_playcount"]/text()').extract_first()
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
