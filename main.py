from crawler import Crawler

noticeList = Crawler().crawlNoticeFromWeb('전체', 10)

print(noticeList[0].title)