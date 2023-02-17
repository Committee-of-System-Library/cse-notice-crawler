from crawler import Crawler
from db import DB

import schedule

crawler = Crawler()
db = DB('127.0.0.1', 3306, 'root', 'sean030502', 'NOTICE_DB') # ip port user password

notice_list = db.get_data('전체', 10)

for notice in notice_list:
    print(notice)