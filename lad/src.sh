#!/bin/sh

cd /home/huang/lad-crawler/lad

echo `date '+%Y-%m-%d %H:%M:%S'` >> runtime.log
scrapy crawl 39new &
scrapy crawl 39health1 &
scrapy crawl 39health2 &
scrapy crawl 39health3 &
scrapy crawl 99yiji &
scrapy crawl 99yiji2 &
scrapy crawl dazhongyangshengwang &
scrapy crawl dazhongyangshengwang2 &
scrapy crawl feihua1 &
scrapy crawl feihua2 &
scrapy crawl shenzhen &
scrapy crawl beijing &
scrapy crawl Urumqi &
scrapy crawl xinjiang &
scrapy crawl lasa &
scrapy crawl lanzhou &
scrapy crawl qinghai &
scrapy crawl kunming &
scrapy crawl neimenggu &
scrapy crawl sichuan &
scrapy crawl guangxi &
scrapy crawl hainan &
scrapy crawl hangzhou &
scrapy crawl jiangsu &
scrapy crawl nanjing &
scrapy crawl jinan

