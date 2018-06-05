# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: http://doc.scrapy.org/en/latest/topics/item-pipeline.html

import pymongo
import random
from scrapy.conf import settings

class NoincrementalPipeline(object):
    def __init__(self):
        self.client = pymongo.MongoClient(host=settings['MONGO_HOST'], port=settings['MONGO_PORT'])
        self.db = self.client[settings['MONGO_DB']]

        # try:
        #     self.db.authenticate(name=settings['USERNAME'], password=settings['PASSWORD'])
        # except TypeError, e:
        #     raise Exception(u'MONGODB数据库用户名或密码错误，认证失败: %s' % e.message)

        coll_name_video = settings['COLLECTION_VIDEO']
        coll_name_broadcast = settings['COLLECTION_BROADCAST']
        coll_broadcast = self.db[coll_name_broadcast]
        coll_video = self.db[coll_name_video]

        self.name_to_coll = dict()
        self.name_to_coll[coll_name_broadcast] = coll_broadcast
        self.name_to_coll[coll_name_video] = coll_video

    def process_item(self, item, spider):
        if not hasattr(item, 'collection'):
            return

        hit_collection = self.name_to_coll.get(item.collection)
        if hit_collection == None:
            return

        if item.collection == settings['COLLECTION_VIDEO']:
            item["visitNum"] = 0
            item["shareNum"] = 0
            item["commnetNum"] = 0
            item["thumpsubNum"] = 0
            item["collectNum"] = 0
            item["num"] = random.randint(1, 100000)
        elif item.collection == settings['COLLECTION_BROADCAST']:
            item["visitNum"] = 0
            item["commnetNum"] = 0
            item["thumpsubNum"] = 0
            item["random_num"] = random.randint(1, 100000)

        hit_collection.insert(dict(item))
        return item
