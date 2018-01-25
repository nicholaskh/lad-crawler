#coding=utf-8
from bs4 import BeautifulSoup

def processText(circleList):
    text = ''
    for i in circleList:
        if i.extract().find('<img') > 0:
            text = text + '$#$' + '\n\r'
        else:
            if i.extract().find('<script') >= 0 or i.extract().find('<style') >= 0:
                continue
            else:
                text = text + BeautifulSoup(i.extract(), "lxml").get_text() + '\n\r'
    return text

def processImg(list_extract):
    soup = BeautifulSoup(list_extract, "lxml")
    if soup.img is not None:
        img_list = []
        if len(soup.img) > 1:
            for i in soup.img:
                img_list.append(i.get('src'))
        else:
            img_list.append(soup.img.get('src'))
    return img_list
