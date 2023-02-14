from crawler import Crawler

crawler = Crawler()

notice_list = crawler.crawl_notice_from_web(amount=-1)

crawler.insert_notice(notice_list)

crawler.close()