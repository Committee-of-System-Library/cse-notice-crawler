import requests
from bs4 import BeautifulSoup

import schedule

import sqlite3


URLs = {
    '전체': 'https://computer.knu.ac.kr/bbs/board.php?bo_table=sub5_1',
    '일반공지': 'https://computer.knu.ac.kr/bbs/board.php?bo_table=sub5_1&sca=%EC%9D%BC%EB%B0%98%EA%B3%B5%EC%A7%80',
    '학사': 'https://computer.knu.ac.kr/bbs/board.php?bo_table=sub5_1&sca=%ED%95%99%EC%82%AC',
    '장학': 'https://computer.knu.ac.kr/bbs/board.php?bo_table=sub5_1&sca=%EC%9E%A5%ED%95%99',
    '심컴': 'https://computer.knu.ac.kr/bbs/board.php?bo_table=sub5_1&sca=%EC%8B%AC%EC%BB%B4',
    '글솝': 'https://computer.knu.ac.kr/bbs/board.php?bo_table=sub5_1&sca=%EA%B8%80%EC%86%9D',
    '대학원': 'https://computer.knu.ac.kr/bbs/board.php?bo_table=sub5_1&sca=%EB%8C%80%ED%95%99%EC%9B%90',
    '대학원 계약학과': 'https://computer.knu.ac.kr/bbs/board.php?bo_table=sub5_1&sca=%EB%8C%80%ED%95%99%EC%9B%90+%EA%B3%84%EC%95%BD%ED%95%99%EA%B3%BC'
}

num = None
link = None
title = None
category = None
createDate = None
content = None


def create_table():
    conn = sqlite3.connect('notice.db')
    c = conn.cursor()

    c.execute('''CREATE TABLE IF NOT EXISTS Notice
                (num INTEGER PRIMARY KEY, link TEXT, title TEXT, category TEXT, createDate DateTime, content LONGTEXT)''')

    conn.commit()
    conn.close()

def connectDB():
    conn = sqlite3.connect('notice.db')
    c = conn.cursor()

    return conn, c

def get_notice(searchCategory='전체', amount=1, *dataTypes):
    global num, link, title, category, createDate, content

    if searchCategory not in URLs:
        raise ValueError('category must be one of 전체, 일반공지, 학사, 장학, 심컴, 글솝, 대학원, 대학원 계약학과')
    
    elif set(dataTypes) - set(['num', 'link', 'title', 'category', 'createDate', 'content']):
        raise ValueError('data_type must be one of num, link, title, category, createDate, content')

    else:
        noticeList = []

        response = requests.get(URLs[searchCategory])
        soup = BeautifulSoup(response.text, 'html.parser')

        limit = int(soup.select_one('tbody tr:not(.bo_notice) td.td_num2').text.strip())

        if amount > limit:
            amount = limit

        if amount <= 15:
            searchList = list(soup.select('tbody tr:not(.bo_notice) td.td_subject div.bo_tit a'))

            for idx in range(amount):
                num = limit - idx
                link = searchList[idx].get('href')

                response = requests.get(link)
                soup = BeautifulSoup(response.text, 'html.parser')

                title = soup.select_one('.bo_v_tit').text.strip()
                category = soup.select_one('.bo_v_cate').text if searchCategory == '전체' else searchCategory
                createDate = '20' + soup.select_one('.if_date').text.replace('작성일 ', '') + ':00'
                content = soup.select_one('#bo_v_con').text.strip().replace('\xa0', '')

                if dataTypes == ():
                    noticeList.append([link, title, category, createDate, content])
                else:
                    noticeList.append([globals()[data] for data in dataTypes])

        else:
            pages = amount // 15 + 2

            for page in range(1, pages):
                response = requests.get(URLs[searchCategory] + '&page=' + str(page))
                soup = BeautifulSoup(response.text, 'html.parser')
                searchList = list(soup.select('tbody tr:not(.bo_notice) td.td_subject div.bo_tit a'))

                if searchList == []:
                    break

                for idx in range(15 if page != pages - 1 else amount % 15):
                    num = limit - (page - 1) * 15 - idx
                    link = searchList[idx].get('href')

                    response = requests.get(link)
                    soup = BeautifulSoup(response.text, 'html.parser')

                    title = soup.select_one('.bo_v_tit').text.strip()
                    category = soup.select_one('.bo_v_cate').text if searchCategory == '전체' else searchCategory
                    createDate = '20' + soup.select_one('.if_date').text.replace('작성일 ', '') + ':00'
                    content = soup.select_one('#bo_v_con').text.strip().replace('\xa0', '')

                    if dataTypes == ():
                        noticeList.append([num, link, title, category, createDate, content])
                    else:
                        noticeList.append([globals()[data] for data in dataTypes])

        return noticeList

def insert_notice(noticeList):
    conn, c = connectDB()

    for notice in noticeList:
        c.execute('INSERT INTO Notice VALUES (?, ?, ?, ?, ?, ?)', notice)

    conn.commit()
    conn.close()

def get_notice_from_db(searchCategory='전체', amount=1, *dataTypes):
    conn, c = connectDB()

    if searchCategory not in URLs:
        raise ValueError('category must be one of 전체, 일반공지, 학사, 장학, 심컴, 글솝, 대학원, 대학원 계약학과')
    
    elif set(dataTypes) - set(['num', 'link', 'title', 'category', 'createDate', 'content']):
        raise ValueError('data_type must be one of num, link, title, category, createDate, content')

    else:
        if dataTypes == ():
            c.execute('SELECT * FROM Notice WHERE category = ? ORDER BY createDate DESC LIMIT ?', (searchCategory, amount))
        else:
            c.execute('SELECT ' + ', '.join(dataTypes) + ' FROM Notice WHERE category = ? ORDER BY createDate DESC LIMIT ?', (searchCategory, amount))

        noticeList = c.fetchall()

        conn.commit()
        conn.close()

        return noticeList

def updateDB():
    conn, c = connectDB()

    c.execute('SELECT num FROM Notice ORDER BY num DESC LIMIT 1')
    lastNum = c.fetchone()[0]

    noticeList = get_notice(amount=30)

    for noticeIndx in range(noticeList[0][0] - lastNum):
        c.execute('INSERT INTO Notice VALUES (?, ?, ?, ?, ?, ?)', noticeList[noticeIndx])


if __name__ == '__main__':
    create_table()