import json
import os

from crawler import Crawler
from notice import *

crawler = Crawler()
url = os.getenv(key='API_URL')

def run():
    notice_list = crawler.crawl_notice_from_web(amount=100)
    response = crawler.send_notice_to_api(url, notice_list)
    print(response)

if __name__ == '__main__':
    run()