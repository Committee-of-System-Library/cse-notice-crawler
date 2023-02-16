import pymysql

from notice import Notice
from crawler import *

class DB:
    def __init__(self, host, port, user, password):
        self.host = host
        self.port = port
        self.user = user
        self.password = password
        self.conn = None
        self.cursor = None

    def _connect_db(self):
        """DB 연결 함수
        """

        self.conn = pymysql.connect(host=self.host, port=self.port, user=self.user, password=self.password, db='NOTICE_DB', charset='utf8', autocommit=True)
        self.cursor = self.conn.cursor()
        self.cursor.execute("USE NOTICE_DB")

    def create_table(self):
        """테이블 생성 함수
        """

        self._connect_db()

        self.cursor.execute('''CREATE TABLE IF NOT EXISTS NOTICE_TABLE
                    (num INTEGER PRIMARY KEY, link TEXT, title TEXT, category TEXT, created_at DateTime, content LONGTEXT, updated_at DateTime DEFAULT NULL, status INTEGER DEFAULT 0)''')
        self.cursor.execute("ALTER TABLE NOTICE_TABLE CONVERT TO CHARSET UTF8")

        self.disconnect_db()

    def insert_notice(self, notice_list: list[Notice]):
        """공지사항 데이터를 DB에 삽입
        """

        self._connect_db()

        self.cursor.executemany(f"INSERT INTO NOTICE_TABLE (num, link, title, category, created_at, content) VALUES (%s, %s, %s, %s, %s, %s)", [(notice.num, notice.link, notice.title, notice.category, notice.created_at, notice.content) for notice in notice_list])

        self.disconnect_db()

    def get_data_from_db(self, search_category: str='전체', amount: int=1) -> list[Notice]:
        """DB에서 데이터를 가져오는 함수
        """

        self._connect_db()

        if search_category == '전체':
            self.cursor.execute(f"SELECT * FROM NOTICE_TABLE ORDER BY num DESC LIMIT {amount}")
        else:
            self.cursor.execute(f"SELECT * FROM NOTICE_TABLE WHERE category = '{search_category}' ORDER BY num DESC LIMIT {amount}")

        data = self.cursor.fetchall()
        self.disconnect_db()

        return data

    def update_db(self):
        """DB를 업데이트 하는 함수
        """

        self._connect_db()

        crawler = Crawler()
        notice_list = crawler.crawl_notice_from_web(amount=10)

        for notice in notice_list:
            self.cursor.execute(f"SELECT num FROM NOTICE_TABLE WHERE num = {notice.num}")
            data = self.cursor.fetchall()

            if len(data) == 0:
                self.cursor.execute(f"INSERT INTO NOTICE_TABLE (num, link, title, category, created_at, content) VALUES ({notice.num}, '{notice.link}', '{notice.title}', '{notice.category}', '{notice.created_at}', '{notice.content}')")

            else:
                self.cursor.execute(f"SELECT * FROM NOTICE_TABLE WHERE num = {notice.num}")
                data = self.cursor.fetchall()

                if data[0][2] != notice.title or data[0][3] != notice.category or data[0][5] != notice.content:
                    self.cursor.execute(f"UPDATE NOTICE_TABLE SET title = '{notice.title}', category = '{notice.category}', content = '{notice.content}', updated_at = '{notice.created_at}', status = 2 WHERE num = {notice.num}")

        self.disconnect_db()

    def disconnect_db(self):
        """DB 연결 해제 함수
        """

        self.conn.close()
        self.cursor = None