import requests
from bs4 import BeautifulSoup

import schedule

import sqlite3
import pymysql


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
created_at = None
content = None


def createTable():
    conn = sqlite3.connect('notice.db')
    c = conn.cursor()

    c.execute('''CREATE TABLE IF NOT EXISTS Notice
                (num INTEGER PRIMARY KEY, link TEXT, title TEXT, category TEXT, created_at DateTime, content LONGTEXT)''')

    conn.commit()
    conn.close()

def connectDB():
    conn = sqlite3.connect('notice.db')
    c = conn.cursor()

    return conn, c

def getNotice(search_category='전체', amount=1, *data_types):
    global num, link, title, category, created_at, content
    
    notice_list = []

    response = requests.get(URLs[search_category])
    soup = BeautifulSoup(response.text, 'html.parser')

    limit = int(soup.select_one('tbody tr:not(.bo_notice) td.td_num2').text.strip())

    if amount > limit or amount < 0:
        amount = limit

    pages = amount // 15 + 2


    for page in range(1, pages):
        response = requests.get(URLs[search_category] + '&page=' + str(page))
        soup = BeautifulSoup(response.text, 'html.parser')
        search_list = list(soup.select('tbody tr:not(.bo_notice) td.td_subject div.bo_tit a'))

        if search_list == []:
            break

        for idx in range(15 if page != pages - 1 else amount % 15):
            num = limit - (page - 1) * 15 - idx
            link = search_list[idx].get('href')

            response = requests.get(link)
            soup = BeautifulSoup(response.text, 'html.parser')

            title = soup.select_one('.bo_v_tit').text.strip()
            category = soup.select_one('.bo_v_cate').text if search_category == '전체' else search_category
            created_at = '20' + soup.select_one('.if_date').text.replace('작성일 ', '') + ':00'
            content = soup.select_one('#bo_v_con').text.strip().replace('\xa0', '')

            if data_types == ():
                notice_list.append([num, link, title, category, created_at, content])
            else:
                notice_list.append([globals()[data] for data in data_types])

    return notice_list

def insertNotice(notice_list):
    conn, c = connectDB()

    for notice in notice_list:
        c.execute('INSERT INTO Notice VALUES (?, ?, ?, ?, ?, ?)', notice)

    conn.commit()
    conn.close()

def getDB(search_category='전체', amount=1, *data_types):
    conn, c = connectDB()

    if data_types == ():
        c.execute('SELECT * FROM Notice WHERE category = ? ORDER BY created_at DESC LIMIT ?', (search_category, amount))
    else:
        c.execute('SELECT ' + ', '.join(data_types) + ' FROM Notice WHERE category = ? ORDER BY created_at DESC LIMIT ?', (search_category, amount))

    notice_list = c.fetchall()

    conn.commit()
    conn.close()

    return notice_list

def updateDB():
    conn, c = connectDB()

    c.execute('SELECT num FROM Notice ORDER BY num DESC LIMIT 1')
    lastNum = c.fetchone()[0]

    notice_list = getNotice(amount=15)

    for noticeIndx in range(notice_list[0][0] - lastNum):
        c.execute('INSERT INTO Notice VALUES (?, ?, ?, ?, ?, ?)', notice_list[noticeIndx])


if __name__ == '__main__':
    createTable()