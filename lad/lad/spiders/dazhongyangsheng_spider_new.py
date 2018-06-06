#coding=utf-8
import scrapy
import re

from ..items import YangshengwangItem
from ..spiders.beautifulSoup import processText
from datetime import datetime
from basespider import BaseTimeCheckSpider

class NewsSpider(BaseTimeCheckSpider):

    name = "dazhongyangshengwangnew"
    dict_news = {'yinshi/changshi':'2_营养饮食_营养养生','yinshi/shipu':'2_饮食食谱_营养养生','yinshi/dapei':'2_饮食搭配_营养养生',
                 'yinshi/cunchu':'2_食材存储_营养养生','yinshi/shanghuo':'2_上火饮食_营养养生','yinshi/tiaoxuan':'2_挑选技巧_营养养生',
                 'yinshi/jinji':'2_禁忌_营养养生',
                 'renqun/nvxing':'2_女性保健_保健人群','renqun/nanxing':'2_男性保健_保健人群','renqun/laoren':'2_老人保健_保健人群',
                 'renqun/ertong':'2_儿童保健_保健人群','renqun/muying':'2_母婴保健_保健人群','renqun/teshu':'2_特殊人群保健_保健人群',
                 'renqun/mingren':'2_名人养生_保健人群',
                 'zhongyi/changshi':'2_中医常识_中医养生','zhongyi/tizhi':'2_体质养生_中医养生','zhongyi/zhongcaoyao':'2_中草药百科_中医养生',
                 'zhongyi/yaoshan':'2_药膳食疗_中医养生','zhongyi/jingluo':'2_经络养生_中医养生',
                 'shenghuoyangsheng/jujia':'2_居家保健_生活保健','shenghuoyangsheng/jianfei':'2_减肥_生活保健','shenghuoyangsheng/meirong':'2_美容_生活保健',
                 'yundong/changshi':'2_运动常识_运动养生','yundong/qicai':'2_运动器材_运动养生','yundong/yingyang':'2_运动营养_运动养生',
                 'yundong/huwai':'2_户外_运动养生','yundong/jianshen':'2_健身_运动养生','yundong/yujia':'2_瑜伽_运动养生',
                 'zixun/xingainian':'1_健康资讯','zixun/baoguang':'1_曝光台','zixun/xinwen':'1_焦点资讯','zixun/hotnews':'1_精彩热点'
                 }
    start_urls = ['http://www.cndzys.com/%s/' % x for x in dict_news.keys()]

    def parse(self, response):

        next_url = None
        if response.xpath('//*[@class=" paging"]/span')[-2].xpath('a/text()').extract_first().encode('utf-8') == '下一页':
            #判断是否是最后一页,不是的话执行下面逻辑
            next_url = response.url.split('index')[0] + response.xpath('//*[@class=" paging"]/span')[-2].xpath('a/@href').extract_first()

        child_urls = response.xpath('//*[@class="con_left"]/div/div/h4/a/@href')
        for infoDiv in child_urls[:-1]:
            n_url = 'http://www.cndzys.com' + infoDiv.extract()
            child_request = scrapy.Request(url=n_url, callback=self.parse_info)
            m_item = YangshengwangItem()
            m_item['is_final_child'] = False
            key_word = re.search('com/(.+)/', response.url).group(1)
            total_str = self.dict_news[key_word]
            m_item["classNum"] = total_str.split('_')[0]
            if m_item["classNum"] == "2":
                m_item['specificName'] = total_str.split('_')[1]
                m_item["className"] = total_str.split('_')[2]
            else:
                m_item["className"] = total_str.split('_')[1]
            child_request.meta['item'] = m_item
            yield child_request

        # 特殊处理最后一个，通过request的meta传递信息
        final_child_url = 'http://www.cndzys.com' + child_urls[-1].extract()
        final_request = scrapy.Request(url=final_child_url, callback=self.parse_info)
        m_item = YangshengwangItem()
        m_item['is_final_child'] = True
        key_word = re.search('com/(.+)/', response.url).group(1)
        total_str = self.dict_news[key_word]
        m_item["classNum"] = total_str.split('_')[0]
        if m_item["classNum"] == "2":
            m_item['specificName'] = total_str.split('_')[1]
            m_item["className"] = total_str.split('_')[2]
        else:
            m_item["className"] = total_str.split('_')[1]
        m_item['next_father_url'] = next_url
        final_request.meta['item'] = m_item
        yield final_request

    def parse_info(self, response):
        item = response.meta['item']
        time = response.xpath('//*[@class="info"]/span/text()')[1].extract().encode("utf-8").split('时间:')[1]

        try:
            time_now = datetime.strptime(time, '%Y-%m-%d %H:%M:%S')
            # 更新将要保存到MONGODB中的时间
            self.update_last_time(time_now)
        except:
            return

        if self.last_time is not None and self.last_time >= time_now:
            print(u'spider: %s 这篇文章已经存在' % self.url)
            return
        # next_requests = list()
        #if should_deep:
        # 表示有新的url
        item["module"] = "健康资讯"
        item["title"] = response.xpath('/html/body/div/div/div/h1/text()').extract_first()
        item["source"] = '大众养生网'
        item["sourceUrl"] = response.url
        item['imageUrls'] = response.xpath('//*[@style="text-align:center;"]/a/img/@src').extract() #提取图片链接
        if len(response.xpath('//*[@style="text-align:center;"]/a/img/@src').extract()) == 0:
            item['imageUrls'] = response.xpath('//*[@style="text-align:center;"]/img/@src').extract()
        item["time"] = response.xpath('//*[@class="info"]/span/text()')[1].extract().split(':')[1].split(' ')[0]

        text_list = response.xpath('//*[@class="content_text"]/*')

        item["text"] = processText(text_list)

        if len(response.xpath('//*[@class=" paging"]/a/text()')) > 0:
            if response.xpath('//*[@class=" paging"]/a/text()')[-1].extract().encode('utf-8') == '下一页':
                n_url = 'http://www.cndzys.com/' + response.xpath('//*[@class=" paging"]/a/@href')[-1].extract()
                yield scrapy.Request(url=n_url, callback=self.parse_info)
        yield item

        # 在最后一个孩子哪儿判断是否需要爬取下一页，如果代码没有执行到这儿，那么说明下一页的时间已经是无效的时间了
        if item['is_final_child'] and item['next_father_url'] is not None:
            yield scrapy.Request(url=item['next_father_url'], callback=self.parse)
