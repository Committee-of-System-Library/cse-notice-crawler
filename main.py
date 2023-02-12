from crawler import Crawler

crawler = Crawler()

notice_list = crawler.get_data_from_DB()

for notice in notice_list:
    print(notice)