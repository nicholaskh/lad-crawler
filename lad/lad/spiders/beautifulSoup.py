#coding=utf-8
from bs4 import BeautifulSoup

def processText(circleList):
    text = ''
    # for i in response.xpath('//*[@class="detail_con"]/p'):
    for i in circleList:
        if i.extract().find('<img') >= 0 and i.extract().find(u'alt="点此购买1"') < 0:
            text = text + '$#$' + '\n\r'
        else:
            if i.extract().find('<script') >= 0 or i.extract().find('<style') >= 0 or i.extract().find('class="weizhi"') >= 0:
                continue
            else:
                text = text + BeautifulSoup(i.extract(), "lxml").get_text(strip=True)
		if len(text) > 10:
			text = text + '\n\r'
    return text

def processImgSep(list_extract):
    img_list = []
    for i in list_extract:
        soup = BeautifulSoup(i.extract(), "lxml")
        if soup.img is not None:
            if len(soup.img) > 1:
                for i in soup.img:
                    if soup.img.get('alt') != u'点此购买1':
                        img_list.append(i.get('src'))
            else:
                if soup.img.get('alt') != u'点此购买1':
                    img_list.append(soup.img.get('src'))
    return img_list

def processImgSep2(list_extract):
    img_list = []
    for i in list_extract:
        soup = BeautifulSoup(i.extract(), "lxml")
        if soup.img is not None:
            if len(soup.img) > 1:
                for i in soup.img:
                    if soup.img.get('alt').encode('utf-8') != '点此购买1':
                        img_list.append('http://www.cpoha.com.cn'+i.get('src'))
            else:
                if soup.img.get('alt').encode('utf-8') != '点此购买1':
                    img_list.append('http://www.cpoha.com.cn'+soup.img.get('src'))

def processImgSep1(list_extract):
    soup = BeautifulSoup(list_extract, "lxml")
    img_list = []
    if soup.img is not None:
        if len(soup.img) > 1:
            for i in soup.img:
                img_list.append('http://www.gzjd.gov.cn' + i.get('src'))
        else:
            img_list.append('http://www.gzjd.gov.cn' + soup.img.get('src'))
    return img_list

def processImg(list_extract):
    soup = BeautifulSoup(list_extract, "lxml")
    img_list = []
    if soup.img is not None:
        if len(soup.img) > 1:
            for i in soup.img:
                img_list.append(i.get('src'))
        else:
            img_list.append(soup.img.get('src'))
    return img_list
