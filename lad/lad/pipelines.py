# -*- coding: utf-8 -*-

import pymongo
import os
import urllib
import scrapy
from scrapy.conf import settings
from scrapy.exceptions import DropItem
from scrapy.pipelines.images import ImagesPipeline
from qiniu import Auth, put_file, etag, urlsafe_base64_encode
import qiniu.config

class LadPipeline(object):


    def __init__(self):
        self.client = pymongo.MongoClient(host=settings['MONGO_HOST'], port=settings['MONGO_PORT'])
        self.db = self.client[settings['MONGO_DB']]

        coll_name_health = settings['COLLECTION_HEALTH']
        coll_name_security = settings['COLLECTION_SECURITY']
        coll_health = self.db[coll_name_health]
        coll_security = self.db[coll_name_security]

        self.name_to_coll = dict()
        self.name_to_coll[coll_name_security] = coll_security
        self.name_to_coll[coll_name_health] = coll_health

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

        hit_collection.insert(dict(item))
        return item

    def processImageUrls(self, item, spider):
            if not hasattr(self, 'qiniu_client'):
                self.qiniu_client = Auth(self.qiniu_access_key, self.qiniu_secret_key)

            new_imgarray = list()

            dir_path = '%s/%s'%(settings['IMAGES_STORE'], spider.name) #本地存储路径
            if not os.path.exists(dir_path):
                os.makedirs(dir_path)

            for image_url in item['imageUrls']:
                list_name = image_url.split('/')
                file_name = list_name[len(list_name)-1]#图片名称

                file_path = '%s/%s' % (dir_path, file_name)

                if os.path.exists(file_name):
                    continue
                with open(file_path,'wb') as file_writer:
                    conn = urllib.urlopen(image_url)#下载图片
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
