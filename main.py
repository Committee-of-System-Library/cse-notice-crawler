from crawler import Crawler

crawler = Crawler()

noticeList = crawler.getDataFromDB(amount=10)

for notice in noticeList:
    print(notice)