# -*- coding: utf-8 -*-
import pymongo
from scrapy.conf import settings
import random

client = pymongo.MongoClient(host=settings['MONGO_HOST'], port=settings['MONGO_PORT'])
db = client[settings['MONGO_DB']]

# TODO 是否应该把对MONGODB的连接对象都保持在spider内部
try:
    db.authenticate(name=settings['USERNAME'], password=settings['PASSWORD'])
except TypeError, e:
    raise Exception(u'MONGODB数据库用户名或密码错误，认证失败: %s' % e.message)

coll = db.broadcast
for i in coll.find():
    i['num'] = random.randint(1, 100000)
    coll.update({"title":i['title']},{"$set": i})
