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
        self.coll = self.db[settings['MONGO_COLL']]

    def process_item(self, item, spider):
        # 配置七牛云属性
        domain = 'http://oojih7o1f.bkt.clouddn.com/'
        access_key = 'wDgkTBIuUn5KnvyFzuMIr8GdC1KCRnN4KABH7dF-'
        secret_key = 'kQUvoiTx0Odyjo1OUudAJXTlGxF1Nhk1eK7YHV1n'
        q = Auth(access_key, secret_key)
        bucket_name = 'ladapp'

        dir_path = '%s/%s'%(settings['IMAGES_STORE'],spider.name) #本地存储路径
        if not os.path.exists(dir_path):
            os.makedirs(dir_path)
        new_imgarray = []
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

                # 七牛云上传图片
                key = image_url.split('/')[-1]
                new_url = domain + key
                # print('hhhhhhhhhh' + new_url)
                new_imgarray.append(new_url)
                # print(new_imgarray)
                token = q.upload_token(bucket_name, key)
                localfile = file_path
                ret, info = put_file(token, key, localfile)
                print(info)
                assert ret['key'] == key
                assert ret['hash'] == etag(localfile)
                os.remove('/home/huang/lad-crawler/lad/None/39new/' + file_name)
        item['image_urls'] = new_imgarray
        self.coll.insert(dict(item))
        return item
