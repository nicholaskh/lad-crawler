# -*- coding: utf-8 -*-

import pymongo
import os
import urllib
import scrapy
from scrapy.conf import settings
from scrapy.exceptions import DropItem
from scrapy.pipelines.images import ImagesPipeline

class LadPipeline(object):

    def __init__(self):
        self.client = pymongo.MongoClient(host=settings['MONGO_HOST'], port=settings['MONGO_PORT'])
        self.db = self.client[settings['MONGO_DB']]
        self.coll = self.db[settings['MONGO_COLL']]

    def process_item(self, item, spider):
        dir_path = '%s/%s'%(settings['IMAGES_STORE'],spider.name) #存储路径
        if not os.path.exists(dir_path):
            os.makedirs(dir_path)
        if len(item['image_urls']) != 0:
            for image_url in item['image_urls']:
                list_name = image_url.split('/')
                file_name = list_name[len(list_name)-1]#图片名称
                # print 'filename',file_name
                file_path = '%s/%s'%(dir_path,file_name)
                # print 'file_path',file_path
                if os.path.exists(file_name):
                    continue
                with open(file_path,'wb') as file_writer:
                    conn = urllib.urlopen(image_url)#下载图片
                    file_writer.write(conn.read())
                file_writer.close()
        self.coll.insert(dict(item))
        return item
