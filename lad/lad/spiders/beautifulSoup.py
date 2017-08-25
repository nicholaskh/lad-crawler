#coding=utf-8
from bs4 import BeautifulSoup

def processText(circleList):
    text = ''
    # for i in response.xpath('//*[@class="detail_con"]/p'):
    for i in circleList:
        if i.extract().find('<img') > 0:
            text = text + '$#$'
        else:
            text = text + BeautifulSoup(i.extract()).get_text()
    return text
