import requests
from bs4 import BeautifulSoup, PageElement

from notice import Notice

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

MAX_NOTICE_SIZE = 15


class Crawler:
    def __init__(self):
        conn = pymysql.connect(host='127.0.0.1', user='root', password='sean030502', charset='utf8', db='notice')
        c = conn.cursor()

        c.execute('USE notice')
        c.execute('''CREATE TABLE IF NOT EXISTS Notice
                    (num INTEGER PRIMARY KEY, link TEXT, title TEXT, category TEXT, created_at DateTime, content LONGTEXT, updated_at DateTime DEFAULT NULL, status INTEGER DEFAULT 0)''')
        c.execute('ALTER TABLE Notice CONVERT TO CHARSET UTF8')

        self.conn = conn
        self.c = c

    def __parse_notice_total_count(self) -> int:
        response = requests.get(URLs['전체'])
        soup = BeautifulSoup(response.text, 'html.parser')

        return int(soup.select_one('tbody tr:not(.bo_notice) td.td_num2').text.strip())

    def __parse_notice_table(self, search_category, page) -> list[PageElement]:
        response = requests.get(URLs[search_category] + '&page=' + str(page))
        soup = BeautifulSoup(response.text, 'html.parser')

        return list(soup.select('tbody tr:not(.bo_notice) td.td_subject div.bo_tit a'))

    def __get_notice_data(self, notice: PageElement) -> Notice:
        link = notice.get('href')
        num = int(link.split('wr_id')[-1].split('&')[0].replace('=', ''))

        response = requests.get(link)
        soup = BeautifulSoup(response.text, 'html.parser')

        title = soup.select_one('.bo_v_tit').text.strip()
        category = soup.select_one('.bo_v_cate').text
        created_at = '20' + soup.select_one('.if_date').text.replace('작성일 ', '') + ':00'
        content = soup.select_one('#bo_v_con').text.strip().replace('\xa0', '')

        return Notice(num, link, title, category, created_at, content)

    def crawl_notice_from_web(self, search_category: str='전체', amount: int=-1) -> list[Notice]:
        """공지사항을 크롤링하는 함수

        Args:
            search_category (str, optional): 크롤링할 공지사항의 카테고리. Defaults to '전체'.
            amount (int, optional): 크롤링할 공지사항의 개수. Defaults to -1.

        Returns:
            list[Notice]: 크롤링한 공지사항 리스트
        """
        
        if amount == 0:
            return []

        notice_list = list()

        notice_total_count = self.__parse_notice_total_count()
        if amount > notice_total_count or amount == -1:
            amount = notice_total_count

        pages = amount // MAX_NOTICE_SIZE + 2

        for page in range(1, pages):
            notice_table = self.__parse_notice_table(search_category, page)

            if page == pages - 1:
                notice_table = notice_table[:amount % MAX_NOTICE_SIZE]

            for notice in notice_table:
                notice_list.append(self.__get_notice_data(notice))

        return notice_list

    def insert_notice(self, notice_list: list[Notice]):
        """공지사항을 DB에 저장하는 함수

        Args:
            notice_list (list[Notice]): 저장할 공지사항 리스트
        """

        for notice in notice_list:
            self.c.execute('INSERT INTO Notice VALUES (%s, %s, %s, %s, %s, %s, %s, %s)', notice.get_data())

    def get_data_from_DB(self, search_category: str='전체', amount: int=1) -> list[Notice]:
        """DB에서 공지사항을 가져오는 함수

        Args:
            search_category (str, optional): 가져올 공지사항의 카테고리. Defaults to '전체'.
            amount (int, optional): 가져올 공지사항의 개수. Defaults to 1.

        Returns:
            list[Notice]: 가져온 공지사항 리스트
        """

        if search_category == '전체':
            self.c.execute('SELECT * FROM Notice ORDER BY num DESC LIMIT %s', (amount,))
        else:
            self.c.execute('SELECT * FROM Notice WHERE category = %s ORDER BY num DESC LIMIT %s', (search_category, amount))

        result = self.c.fetchall()

        return result

    def update_DB(self):
        """DB를 업데이트하는 함수
        """

        self.c.execute('SELECT num FROM Notice ORDER BY num DESC LIMIT 1')
        last_num = self.c.fetchone()[0]

        notice_list = crawl_notice_from_web(amount=15)

        for notice_index in range(notice_list[0][0] - last_num):
            self.c.execute('INSERT INTO Notice VALUES (%s, %s, %s, %s, %s, %s, %s, %s)'.format(notice_list[notice_index]))

    def close(self):
        """DB와의 연결을 종료하는 함수
        """

        self.conn.commit()
        self.conn.close()