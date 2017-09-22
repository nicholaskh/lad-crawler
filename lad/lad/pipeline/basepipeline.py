# -*- coding: utf-8 -*-


class BasePipeline(object):

    def __init__(self):
        pass

    def open_spider(self, spider):
        print u'spider:%s start....' % spider.name

    def close_spider(self, spider):
        print u'spider:%s close....' % spider.name

        if hasattr(spider, 'update_last_time_to_mongodb'):
            spider.update_last_time_to_mongodb()



# 没有必要在pipeline中设置mongo client，这个属性应该再spider的基类中

# class BaseMongoPipline(BasePipeline):
#
#     def __init__(self):
#         self.client = pymongo.MongoClient(host=settings['MONGO_HOST'], port=settings['MONGO_PORT'])
#         self.db = self.client[settings['MONGO_DB']]
#
#     def open_spider(self, spider):
#         BasePipeline.open_spider(self, spider)
#         spider.db = self.db
#         spider.client = self.client
#
#     def close_spider(self, spider):
#         BasePipeline.close_spider(self, spider)
#         # TODO 是否close client？
#
#
# class LastTimePipLine(BaseMongoPipline):
#
#     def open_spider(self, spider):
#         print '88888888888'
#         BaseMongoPipline.open_spider(self, spider)
#
#         coll_info = self.client[settings['COLLECTION_SPIDER_INFO']]
#         query = dict()
#         query['name'] = spider.name
#         res = coll_info.find(query)
#         if res is None:
#             spider.warning(u'没有last_time')
#             spider.last_time = datetime.strptime('1990-1-1', '%Y-%m-%d')
#             return
#
#         last_time = res.get('last_time')
#         if last_time is None:
#             spider.warning(u'没有last_time')
#             spider.last_time = datetime.strptime('1990-1-1', '%Y-%m-%d')
#             return
#
#         try:
#             last_time = datetime.strptime(last_time, '%Y-%m-%d')
#             spider.last_time = last_time
#             return
#         except:
#             pass
#
#         try:
#             last_time = datetime.strptime(last_time, '%Y-%m-%d %H:%M')
#             spider.last_time = last_time
#             return
#         except:
#             pass
#
#         spider.warning(u'没有last_time')
#         spider.last_time = datetime.strptime('1990-1-1', '%Y-%m-%d')
#         print spider.last_time
#
