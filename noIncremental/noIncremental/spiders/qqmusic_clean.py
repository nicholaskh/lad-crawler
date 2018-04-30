# -*- coding: utf-8 -*-

import scrapy
import pymongo

from scrapy.conf import settings
from ..util.log import LogUtil


class QQCleanSpider(scrapy.Spider):
    name = "qqmusic_clean"
    def __init__(self):
        self.log = LogUtil.newLogger(self.name)
        # 初始化与MONGODB的连接
        self.__connect = pymongo.MongoClient(host=settings['MONGO_HOST'], port=settings['MONGO_PORT'])
        self.__db = self.__connect[settings['MONGO_DB']]

        try:
            self.__db.authenticate(name=settings['USERNAME'], password=settings['PASSWORD'])
        except TypeError as e:
            raise Exception(u'MONGODB数据库用户名或密码错误，认证失败: %s' % e.message)

        self.__coll_info = self.get_collection(settings['COLLECTION_BROADCAST'])


    def get_collection(self, name):
        '''
            获取数据库中的某个collection
        :param name:
        :return:
        '''
        if name == "":
            return None

        return self.__db[name]

    def log_warning(self, message):
        self.log.warning(message)

    def log_error(self, message):
        self.log.error(message)

    def log_info(self, message):
        self.log.info(message)


    def start_requests(self):
        query = dict()
        query['source'] = "qq音乐"
        res = self.__coll_info.find(query)
        if res is None or res.count() == 0:
            self.log_info(u"找不到数据")
            return
        for each in res:
            query = dict()
            update = dict()
            value = dict()
            query['_id'] = each.get('_id')
            update['$set'] = value
            broadcast_url = each.get('broadcast_url')
            broadcast_url = broadcast_url.replace("ws", "dl")
            value['broadcast_url'] = broadcast_url
            req = scrapy.Request(url=broadcast_url, callback=self.parse)
            req.meta['query'] = query
            req.meta['update'] = update
            yield req

    def parse(self, response):
        query = response.meta['query']
        update = response.meta['update']
        if response.status == 200:
            self.__coll_info.update_one(query, update, upsert=True)
        else:
            self.__coll_info.delete_one(query)

