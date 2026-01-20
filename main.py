import sys
import os
from datetime import datetime
from crawler import Crawler
from notice import *

crawler = Crawler()
url = os.environ['API_URL']
noticeCnt = os.environ['NOTICE_CNT']
recruitingCnt = os.environ['RECRUITING_CNT']
employmentCnt = os.environ['EMPLOYMENT_CNT']

def run(typeSelect: str):
    #
    # Start Function
    #
    # Parameter)
    #   typeSelect: 가져올 공지 종류 선택 (공지사항 / 학부인재모집 / 취업정보)
    #
    match (typeSelect):
        case '-Notice':
            print(f'\n{datetime.now()} - Start crawling ({typeSelect[1:]})')
            noticeList = crawler.get_all_notice(type='공지사항', noticeCnt=int(noticeCnt))
        case '-Recruiting':
            print(f'\n{datetime.now()} - Start crawling ({typeSelect[1:]})')
            noticeList = crawler.get_all_notice(type='학부인재모집', noticeCnt=int(recruitingCnt))
        case '-Employment':
            print(f'\n{datetime.now()} - Start crawling ({typeSelect[1:]})')
            noticeList = crawler.get_all_notice(type='취업정보', noticeCnt=int(employmentCnt))
        case _:
            print("Usage:", sys.argv[0], "-[ Notice | Recruiting | Employment ]\n")
            return
    print(f'{datetime.now()} - Finish crawling ({typeSelect[1:]})')
    response = crawler.send_notice_to_api(url, noticeList)
    print(f'{datetime.now()} - Finish sending ({typeSelect[1:]}) - {response}')

if __name__ == '__main__':
    if (len(sys.argv) != 2):
        print("Usage:", sys.argv[0], "-[ Notice | Recruiting | Employment ]\n")
    else:
        run(sys.argv[1])
