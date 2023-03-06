import schedule
import json

from crawler import Crawler
from notice import *

crawler = Crawler()
url = 'http://52.78.131.123'

def run():
    notice_list = crawler.crawl_notice_from_web(amount=10)
    response = crawler.send_notice_to_api(url, notice_list)
    print(response)

if __name__ == '__main__':
    run()
    schedule.every(5).minutes.do(run)

    while True:
        schedule.run_pending()
        