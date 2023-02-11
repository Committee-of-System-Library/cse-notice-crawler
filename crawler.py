import requests
from bs4 import BeautifulSoup, PageElement

from notice import Notice

import schedule

import sqlite3
# import pymysql


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

MAX_NOTICE_SIZE = 15

def createTable():
    conn = sqlite3.connect('notice.db')
    c = conn.cursor()

    c.execute('''CREATE TABLE IF NOT EXISTS Notice
                (num INTEGER PRIMARY KEY, link TEXT, title TEXT, category TEXT, created_at DateTime, content LONGTEXT, updated_at DateTime DEFAULT NULL, status INTEGER DEFAULT 0)''')

    conn.commit()
    conn.close()

def connectDB():
    conn = sqlite3.connect('notice.db')
    c = conn.cursor()

    return conn, c

def parseNoticeTotalCount() -> int:
    response = requests.get(URLs['전체'])
    soup = BeautifulSoup(response.text, 'html.parser')

    return int(soup.select_one('tbody tr:not(.bo_notice) td.td_num2').text.strip())

def parseNoticeTableFromPage(searchCategory, page) -> list[PageElement]:
    response = requests.get(URLs[searchCategory] + '&page=' + str(page))
    soup = BeautifulSoup(response.text, 'html.parser')

    return list(soup.select('tbody tr:not(.bo_notice) td.td_subject div.bo_tit a'))

def getNoticeDataFromNotice(notice: PageElement):
    link = notice.get('href')
    num = int(link.split('wr_id')[-1].split('&')[0].replace('=', ''))

    response = requests.get(link)
    soup = BeautifulSoup(response.text, 'html.parser')

    title = soup.select_one('.bo_v_tit').text.strip()
    category = soup.select_one('.bo_v_cate').text
    created_at = '20' + soup.select_one('.if_date').text.replace('작성일 ', '') + ':00'
    content = soup.select_one('#bo_v_con').text.strip().replace('\xa0', '')

    return Notice(num, link, title, category, created_at, content)

def crawlNoticeFromWeb(searchCategory: str='전체', amount: int=-1):
    """공지사항을 크롤링하는 함수

    Args:
        searchCategory (str, optional): 크롤링할 공지사항의 카테고리. Defaults to '전체'.
        amount (int, optional): 크롤링할 공지사항의 개수. Defaults to -1.

    Returns:
        list[Notice]: 크롤링한 공지사항 리스트
    """
    
    if amount == 0:
        return []

    noticeList = list()

    noticeTotalCount = parseNoticeTotalCount()
    if amount > noticeTotalCount or amount == -1:
        amount = noticeTotalCount

    pages = amount // MAX_NOTICE_SIZE + 2

    for page in range(1, pages):
        noticeTable = parseNoticeTableFromPage(searchCategory, page)

        if page == pages - 1:
            noticeTable = noticeTable[:amount % MAX_NOTICE_SIZE]

        for notice in noticeTable:
            noticeList.append(getNoticeDataFromNotice(notice))

    return noticeList

def insertNotice(noticeList):
    conn, c = connectDB()

    for notice in noticeList:
        c.execute('INSERT INTO Notice VALUES (?, ?, ?, ?, ?, ?, ?, ?)', notice.getList())

    conn.commit()
    conn.close()

def getDataFromDB(searchCategory='전체', amount=1):
    conn, c = connectDB()

    if searchCategory == '전체':
        c.execute('SELECT * FROM Notice ORDER BY num DESC LIMIT ?', (amount,))
    else:
        c.execute('SELECT * FROM Notice WHERE category = ? ORDER BY num DESC LIMIT ?', (searchCategory, amount))

    result = c.fetchall()

    conn.close()

    return result

def updateDB():
    conn, c = connectDB()

    c.execute('SELECT num FROM Notice ORDER BY num DESC LIMIT 1')
    lastNum = c.fetchone()[0]

    noticeList = crawlNoticeFromWeb(amount=15)

    for noticeIndx in range(noticeList[0][0] - lastNum):
        c.execute('INSERT INTO Notice VALUES (?, ?, ?, ?, ?, ?, ?, ?)', noticeList[noticeIndx])


if __name__ == '__main__':
    createTable()

    noticeList = crawlNoticeFromWeb(amount=-1)
    insertNotice(noticeList)