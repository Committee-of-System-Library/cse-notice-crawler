from crawler import Crawler
from db import DB

import schedule

crawler = Crawler()
db = DB('localhost', 3306, 'root', 'sean030502', 'NOTICE_DB') # ip port user password

notice_list = db.get_data_from_db('전체', 10)

for notice in notice_list:
    print(notice)