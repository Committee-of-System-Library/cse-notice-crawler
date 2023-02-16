from crawler import Crawler
from db import DB

crawler = Crawler()
db = DB('', 3306, '', '', '') # ip port user password

notice_list = db.get_data_from_db('전체', 10)

for notice in notice_list:
    print(notice)