#!/bin/sh

cd /home/huang/lad-crawler/lad

echo `date '+%Y-%m-%d %H:%M:%S'` >> runtime.log
scrapy crawl 39newnew &
scrapy crawl 39health1new &
scrapy crawl 39health2new &
scrapy crawl 39health3new &
scrapy crawl 99yijinew &
scrapy crawl 99yiji2new &
scrapy crawl dazhongyangshengwangnew &
scrapy crawl dazhongyangshengwang2 & #不变
scrapy crawl feihua1new &
scrapy crawl feihua2new &
scrapy crawl shenzhennew &
scrapy crawl beijing & # 不变
scrapy crawl Urumqi & # 不变
scrapy crawl xinjiang &
scrapy crawl lasanew &
scrapy crawl lanzhounew &
scrapy crawl qinghai & # 不变
scrapy crawl kunming & # 不变
scrapy crawl neimenggunew &
scrapy crawl sichuannew &
scrapy crawl guangxinew &
scrapy crawl hainan & # 不变
scrapy crawl jiangsu & # 不变
scrapy crawl nanjing & # 不变
scrapy crawl jinannew


