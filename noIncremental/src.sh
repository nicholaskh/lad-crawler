#!/bin/sh

cd /home/huang/noIncremental
echo `date '+%Y-%m-%d %H:%M:%S'` >> runtime.log
scrapy crawl broadtest &
scrapy crawl broadtest2 &
scrapy crawl lanren &
scrapy crawl lanren2 &
scrapy crawl zhongbroad &
scrapy crawl zhongbroad2
