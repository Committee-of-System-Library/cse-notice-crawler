from crawler import Crawler
from db import DB

crawler = Crawler()
db = DB('127.0.0.1', 3306, 'root', 'sean030502') # ip port user password

db.update_db()