# -*- coding: utf-8 -*-

import pymongo
import os
import urllib2
from scrapy.conf import settings
from qiniu import Auth, put_file
from pipeline.basepipeline import BasePipeline
import random

class LadPipeline(BasePipeline):

    def __init__(self):
        self.client = pymongo.MongoClient(host=settings['MONGO_HOST'], port=settings['MONGO_PORT'])
        self.db = self.client[settings['MONGO_DB']]

        # TODO 是否应该把对MONGODB的连接对象都保持在spider内部
        # try:
        #     self.db.authenticate(name=settings['USERNAME'], password=settings['PASSWORD'])
        # except TypeError, e:
        #     raise Exception(u'MONGODB数据库用户名或密码错误，认证失败: %s' % e.message)

        coll_name_health = settings['COLLECTION_HEALTH']
        coll_name_security = settings['COLLECTION_SECURITY']
        coll_name_yanglao = settings['COLLECTION_YANGLAO']
        coll_name_dailynews = settings['COLLECTION_DAILYNEWS']
        coll_health = self.db[coll_name_health]
        coll_security = self.db[coll_name_security]
        coll_yanglao = self.db[coll_name_yanglao]
        coll_dailynews = self.db[coll_name_dailynews]

        self.name_to_coll = dict()
        self.name_to_coll[coll_name_security] = coll_security
        self.name_to_coll[coll_name_health] = coll_health
        self.name_to_coll[coll_name_yanglao] = coll_yanglao
        self.name_to_coll[coll_name_dailynews] = coll_dailynews

        # 配置七牛云属性
        self.qiniu_domain = settings['QINIU_DOMAIN']
        self.qiniu_access_key = settings['QINIU_ACCESS_KEY']
        self.qiniu_secret_key = settings['QINIU_SECRET_KEY']

        self.qiniu_bucket_name = 'ladapp'

    def process_item(self, item, spider):
        if not hasattr(item, 'collection'):
            return

        hit_collection = self.name_to_coll.get(item.collection)
        if hit_collection == None:
            return

        if 'imageUrls' in item:
            self.processImageUrls(item, spider)

        item['num'] = random.randint(1, 100000)
        hit_collection.insert(dict(item))
        return item

    def processImageUrls(self, item, spider):
            if not hasattr(self, 'qiniu_client'):
                self.qiniu_client = Auth(self.qiniu_access_key, self.qiniu_secret_key)

            new_imgarray = list()

            # 本地存储路径
            dir_path = '%s/%s' % (settings['IMAGES_STORE'], spider.name)
            if not os.path.exists(dir_path):
                os.makedirs(dir_path)

            if item['imageUrls'] is not None:
                for image_url in item['imageUrls']:
                    list_name = image_url.split('/')
                    # 图片名称
                    file_name = list_name[len(list_name)-1]

                    file_path = '%s/%s' % (dir_path, file_name)

                    if os.path.exists(file_name):
                        continue
                    with open(file_path,'wb') as file_writer:
                        # 下载图片
                        headers = {
                            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/55.0.2883.75 Safari/537.36'}
                        req = urllib2.Request(url=image_url, headers=headers)
                        conn = urllib2.urlopen(req)
                        file_writer.write(conn.read())

                    # 七牛云上传图片
                    key = image_url.split('/')[-1]
                    new_url = self.qiniu_domain + key
                    new_imgarray.append(new_url)
                    token = self.qiniu_client.upload_token(self.qiniu_bucket_name, key)
                    put_file(token, key, file_path)

                    os.remove(file_path)
            item['imageUrls'] = new_imgarray
            return item
