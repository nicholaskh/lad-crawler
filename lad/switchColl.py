#!/usr/bin/python
# -*- coding: utf-8 -*-

from pymongo import MongoClient
from scrapy.conf import settings

# 健康collection
COLL_HEALTH_BACKUP = 'health_backup'
COLL_HEALTH = 'health'
# 咨询collection
COLL_SECURITY_BACKUP = 'security_backup'
COLL_SECURITY = 'security'
# 数据库名
DB_NAME = 'news'


#连接到数据库
conn = MongoClient(host=settings['MONGO_HOST'], port=settings['MONGO_PORT'])
news = conn[DB_NAME]
try:
	news.authenticate(name=settings['USERNAME'], password=settings['PASSWORD'])
except TypeError, e:
	raise Exception(u'MONGODB数据库用户名或密码错误，认证失败: %s' % e.message)
news.drop_collection("health")
news.drop_collection("security")

coll_names = news.collection_names()

if COLL_HEALTH_BACKUP not in coll_names:
	print u'没有%s这个collection' % COLL_HEALTH_BACKUP
	exit(1)

if COLL_SECURITY_BACKUP not in coll_names:
	print u'没有%s这个collection' % COLL_SECURITY_BACKUP
	exit(1)

coll_health_backup = news[COLL_HEALTH_BACKUP]
coll_security_backup = news[COLL_SECURITY_BACKUP]

try:
	coll_health_backup.rename(COLL_HEALTH, dropTarget=True)
	coll_security_backup.rename(COLL_SECURITY, dropTarget=True)
except Exception, e:
	print u'切换失败: %s' % str(e)
