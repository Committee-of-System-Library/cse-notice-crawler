import schedule

from crawler import Crawler

crawler = Crawler()
url = 'https://httpbin.org/post'

def run():
    notice_list = crawler.crawl_notice_from_web(amount=100)
    response = crawler.send_notice_to_api(url, notice_list)
    print(response)

schedule.every(5).minutes.do(run)

while True:
    schedule.run_pending()