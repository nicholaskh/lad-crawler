# coding=utf-8
import scrapy
import re

from ..items import VideoItem


class newsSpider(scrapy.Spider):
    name = "shanchuanxing"
    start_urls = ['https://mp.weixin.qq.com/s?__biz=MzIzMTcyMzY4OA==&mid=2247483927&idx=1&sn=473d9c9db8f932bd2c6a460da9dc08a6&scene=21#wechat_redirect']

    def parse(self, response):
        hrefs = response.xpath('//section[@style="white-space: normal; box-sizing: border-box; background-color: rgb(255, 255, 255);"]//a/@href').extract()
        titles_ori = response.xpath('//section[@style="white-space: normal; box-sizing: border-box; background-color: rgb(255, 255, 255);"]//strong/text()'
                                    ' | //section[@style="white-space: normal; box-sizing: border-box; background-color: rgb(255, 255, 255);"]//span/text()'
                                    ' | //section[@style="white-space: normal; box-sizing: border-box; background-color: rgb(255, 255, 255);"]//a/text()').extract()
        titles = []
        for title in titles_ori:
            if u"第" in title:
                titles.append(title)

        for href, title in zip(hrefs, titles):
            item = VideoItem()
            item['edition'] = re.findall(u'第(.*?)集', title)[0]
            item['sourceUrl'] = href
            item['title'] = title
            if "qq.com" in href:
                req = scrapy.Request(url=href, callback=self.parse_tencent)
                req.meta['item'] = item
                yield req
            elif "xiyou" in href:
                vid = href.split('/')[-1].split('.')[0][2:]
                url = "http://xiyou.cctv.com/interface/index?videoId=" + vid
                req = scrapy.Request(url=url, callback=self.parse_xiyou)
                req.meta['item'] = item
                yield req
            elif "cntv" in href:
                req = scrapy.Request(url=href, callback=self.parse_cntv_pid)
                req.meta['item'] = item
                yield req

    def parse_tencent(self, response):
        page_url = response.url
        vid = page_url.split('/')[-1].split('.')[0]
        url = "https://v.qq.com/iframe/player.html?vid=" + vid + "&tiny=0&auto=0"
        # title_ori = response.xpath('//div[@class="mod_intro"]/div/h1/text()').extract()[0]
        # title = ""
        # for i in range(len(title_ori)):
        #     if title_ori[i] != '\n':
        #         if title_ori[i] != ' ':
        #             if title_ori[i] != '\t':
        #                 title = title + title_ori[i]
        item = response.meta['item']
        item["module"] = "户外旅游"
        item['className'] = "山川行"
        item["url"] = url
        item["source"] = "腾讯视频"
        item["poster"] = None
        yield item

    def parse_cntv_pid(self, response):
        pid = re.findall('videoCenterId","(.+)"', response.text)[0]
        info_url = "http://vdn.apps.cntv.cn/api/getHttpVideoInfo.do?pid=" + pid
        req = scrapy.Request(url=info_url, callback=self.parse_cntv_info)
        req.meta['item'] = response.meta['item']
        yield req

    def parse_cntv_info(self, response):
        item = response.meta['item']
        item["module"] = "户外旅游"
        item['className'] = "山川行"
        item["source"] = "中国网络电视台CNTV"
        urls = re.findall('jpg","url":"(.*?)"', response.text)
        # 取最后的清晰度
        last_num = 1000
        urls_high = []
        for i in range(0, urls.__len__())[::-1]:
            num = int(urls[i].split('-')[-1].split('.')[0], 10)
            if num > last_num:
                urls_high = urls[i + 1:]
                break
            elif i == 0:
                urls_high = urls
                break
            else:
                last_num = num
        url = ""
        for each in urls_high:
            url = url + each + ","
        url = url.strip(',')
        item["url"] = url
        item["poster"] = None
        yield item

    def parse_xiyou(self, response):
            item = response.meta['item']
            item["module"] = "户外旅游"
            item['className'] = "山川行"
            item["source"] = "中国网络电视台CCTV"
            url_ori = re.findall('videoFilePathHD":"(.*?)"', response.text)[0]
            head_url = url_ori.split('#')[0].replace('\\', '')
            video_num = len(url_ori.split('#')[-1].split('_'))
            url = ""
            for i in range(1, video_num + 1):
                url = url + head_url + "-" + str(i) + ".mp4,"
            item["url"] = url.strip(',')
            item["poster"] = None
            yield item
