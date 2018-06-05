# -*- coding: utf-8 -*-

import scrapy
import pymongo

from scrapy.conf import settings
from datetime import datetime
from ..util.log import LogUtil


class BaseSpider(scrapy.Spider):

    def __init__(self):
        self.log = LogUtil.newLogger(self.name)

    def log_warning(self, message):
        self.log.warning(message)

    def log_error(self, message):
        self.log.error(message)

    def log_info(self, message):
        self.log.info(message)

    # TODO: 有时间后再考虑加上全局的异常捕获
    # @staticmethod
    # def guard(func):
    #     '''
    #         统一处理spider出错情况，打印出错日志信息
    #     '''
    #     def _parse(self, response):
    #         try:
    #             func(self, response)
    #         except Exception, e:
    #             pass
    #     return _parse


class BaseMongoSpider(BaseSpider):

    def __init__(self):
        BaseSpider.__init__(self)
        # 初始化与MONGODB的连接
        self.__connect = pymongo.MongoClient(host=settings['MONGO_HOST'], port=settings['MONGO_PORT'])
        self.__db = self.__connect[settings['MONGO_DB']]

        try:
            self.__db.authenticate(name=settings['USERNAME'], password=settings['PASSWORD'])
        except TypeError, e:
            raise Exception(u'MONGODB数据库用户名或密码错误，认证失败: %s' % e.message)

    def get_collection(self, name):
        '''
            获取数据库中的某个collection
        :param name:
        :return:
        '''
        if name == "":
            return None

        return self.__db[name]


class BaseTimeCheckSpider(BaseMongoSpider):

    def __init__(self):

        BaseMongoSpider.__init__(self)
        self.__coll_info = self.get_collection(settings['COLLECTION_SPIDER_INFO'])

        query = dict()
        query['name'] = self.name
        res = self.__coll_info.find(query)
        if res is None:
            self.log.warning(u'spider: %s 在MONOGODB中没有last_time' % self.name)
            self.last_time = datetime.strptime('1990-1-1', '%Y-%m-%d')
            self.next_last_time = self.last_time
            return

        if res.count() > 1:
            self.log_error('mongodb 中存在了重名的spider: %s' % self.name)
            raise Exception('mongodb 中存在了重名的spider: %s' % self.name)

        if res.count() == 0:
            self.log_warning(u'spider: %s 在MONGODB没有last_time' % self.name)
            self.last_time = datetime.strptime('2018-4-15', '%Y-%m-%d')
            self.next_last_time = self.last_time
            return

        last_time = res[0].get('last_time')
        if last_time is None:
            self.log_warning(u'spider: %s 在MONOGODB中没有last_time' % self.name)
            self.last_time = datetime.strptime('1990-1-1', '%Y-%m-%d')
            self.next_last_time = self.last_time
            return

        print last_time
        if isinstance(last_time, datetime):
            self.last_time = last_time
            self.next_last_time = self.last_time
            return

        self.last_time = datetime.strptime('1990-1-1', '%Y-%m-%d')
        self.next_last_time = self.last_time

    def update_last_time_to_mongodb(self):
        '''
            不要在其他地方调用它，除非你真的有必要
        :return:
        '''

        query = dict()
        query['name'] = self.name

        update = dict()
        value = dict()
        update['$set'] = value
        value['last_time'] = self.next_last_time
        self.__coll_info.update_one(query, update, upsert=True)

    def update_last_time(self, new_time):
        '''
            更新last time，此值在spider停止后，更新到MONGODB中
            只有合法(datetime类型，大于next_last_time)的时间才能更新成功
        :param new_time:
        :return:
        '''
        if new_time is None or new_time == '':
            raise Exception('illegal parameters')

        if not isinstance(new_time, datetime):
            raise Exception('it is not a object of datetime')

        if self.next_last_time >= new_time:
            return

        self.next_last_time = new_time

    def start_requests(self):
        if not hasattr(self, 'last_time'):
            self.log_warning(u'spider: %s 没有last_time这个属性，但继承了BaseTimeCheckSpider这个类' % self.name)
            return

        if not isinstance(self.last_time, datetime):
            self.log_warning(u'spider: %s last_time这个属性不是datetime类型' % self.name)
            return

        return BaseMongoSpider.start_requests(self)

    def is_valid_time(self, new_time):
        '''
            检查时间是否在有效时间内
            paTime： datetime 或 basestring 型
        '''
        if isinstance(new_time, datetime):
            return self.last_time > new_time
        elif isinstance(new_time, basestring):
            try:
                t = datetime.strptime(new_time, '%Y-%m-%d %H:%M')
                return self.last_time > t
            except:
                pass

            try:
                t = datetime.strptime(new_time, '%Y-%m-%d')
                return self.last_time > t
            except:
                pass

        return False
