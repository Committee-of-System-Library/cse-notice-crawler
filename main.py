import json
import os
from datetime import datetime

from crawler import Crawler
from notice import *

crawler = Crawler()
# url = os.environ['API_URL']

def run():
    print(f'{datetime.now()} - Start crawling')
    notice_list = crawler.crawl_notice_from_web(amount=100)
    print(f'{datetime.now()} - Finish crawling')
    response = crawler.send_notice_to_api(url, notice_list)
    print(f'{datetime.now()} - Finish sending - {response}')

if __name__ == '__main__':
    notice_list = crawler.crawl_notice_from_web(amount=10)
    for notice in notice_list:
        print(notice.__dict__)