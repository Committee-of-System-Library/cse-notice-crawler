from crawler import Crawler
from db import DB

crawler = Crawler()
db = DB('<ip>', 1234, 'root', 'pw') # ip port user password

db.create_table()

notice_list = crawler.crawl_notice_from_web(amount=1000)

db.insert_notice(notice_list)