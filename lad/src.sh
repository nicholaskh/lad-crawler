#!/bin/sh

cd /home/huang/10.24/lad-crawler/lad

echo `date '+%Y-%m-%d %H:%M:%S'` >> runtime.log
scrapy crawl 39newnew &
scrapy crawl 39health1new &
scrapy crawl 39health2new &
scrapy crawl 39health3new &
scrapy crawl 39health4new &
scrapy crawl 39health5new &
scrapy crwal 39health6new &
scrapy crwal 39health7new &
scrapy crwal 39health8new &
scrapy crawl feihua1new &
scrapy crawl feihua2new &
scrapy crawl 99yijinew &
scrapy crawl 99yiji2new &
scrapy crawl dazhongyangshengwangnew &
scrapy crawl dazhongyangshengwang2 &
scrapy crawl yanhuang2 &
scrapy crawl yanhuang3 &
scrapy crawl yanhuang4 &
scrapy crawl 99yangshengwangnew &
scrapy crawl 99yangshengwangnew2 &
scrapy crawl shenzhennew &
scrapy crawl beijingnew &
scrapy crawl lasanew &
scrapy crawl lanzhounew &
scrapy crawl qinghainew &
scrapy crawl kunmingnew &
scrapy crawl neimenggunew &
scrapy crawl sichuannew &
scrapy crawl guangxinew &
scrapy crawl jiangsunew &
scrapy crawl nanjingnew &
scrapy crawl jinannew &
scrapy crawl hangzhou_new

