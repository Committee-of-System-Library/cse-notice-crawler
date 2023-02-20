from crawler import Crawler

crawler = Crawler()

url = 'https://httpbin.org/post'

notice_list = crawler.crawl_notice_from_web(amount=10)

response = crawler.send_notice_to_api(url, notice_list)

print(response.json())