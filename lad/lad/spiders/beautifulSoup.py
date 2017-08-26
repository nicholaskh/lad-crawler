#coding=utf-8
from bs4 import BeautifulSoup

def processText(circleList):
    text = ''
    # for i in response.xpath('//*[@class="detail_con"]/p'):
    for i in circleList:
        if i.extract().find('<img') > 0:
            text = text + '\n\r' + '$#$' + '\n\r'
        else:
            if i.extract().find('<script') >= 0 or i.extract().find('<style') >= 0:
                continue
            else:
                text = text + BeautifulSoup(i.extract()).get_text() + '\n\r'
    return text
