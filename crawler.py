import requests
from bs4 import BeautifulSoup
import re

from notice import *

URLs = {
        '공지사항': 'https://cse.knu.ac.kr/bbs/board.php?bo_table=sub5_1&page=',
        '학부인재모집': 'https://cse.knu.ac.kr/bbs/board.php?bo_table=sub5_3_a&page=',
        '취업정보': 'https://cse.knu.ac.kr/bbs/board.php?bo_table=sub5_3_b&page=',
    }

CATEGORY_ALIAS = {
    '전체' : 'ALL',
    '일반공지' : 'NORMAL',
    '학사' : 'STUDENT',
    '장학' : 'SCHOLARSHIP',
    '심컴' : 'SIM_COM',
    '글솝' : 'GL_SOP',
    '인컴' : 'SIM_COM',
    '대학원' : 'GRADUATE_SCHOOL',
    '대학원 계약학과' : 'GRADUATE_CONTRACT'
}

MAX_COUNT_OF_NOTICE_PER_PAGE = 0

class Crawler:
    def __get_max_count_of_notice_per_page(self, type: str):
        #
        # 페이지 하나에 최대 몇 개의 공지사항이 들어있는지 확인하기
        # 모든 페이지의 최대 공지 수는 동일하고, 1번 페이지에 가장 많은 공지가 존재하므로, 1번 페이지만 확인합니다.
        # 페이지 구조 변경에 대응하며, MAX_COUNT_OF_NOTICE_PER_PAGE 전역변수를 조작합니다.
        # 
        # Parameter)
        #   type: 가져와야 할 공지사항 종류 (공지사항 / 학부인재모집 / 취업정보)
        #
        # Result)
        #   None
        #
        global MAX_COUNT_OF_NOTICE_PER_PAGE
        response = requests.get(URLs[type] + str(1))
        soup = BeautifulSoup(response.text, 'html.parser').select_one('tbody')
        if (self.__isEmpty(soup) == 1):
            MAX_COUNT_OF_NOTICE_PER_PAGE = 0
        else:
            MAX_COUNT_OF_NOTICE_PER_PAGE = len(soup.find_all('tr'))
        
    def __get_raw_page_of_notice(self, type:str, pageNum: int) -> BeautifulSoup:
        #
        # 공지사항 페이지에서 Raw data 가져오기 
        # 하나의 페이지에 대한 Raw data 가져옵니다.
        #
        # Parameter)
        #   type: 가져와야 할 공지사항 종류 (공지사항 / 학부인재모집 / 취업정보)
        #   pageNum: 가져올 공지사항의 Page Number
        #   
        # Return) 가져온 공지사항 html code (Type: BeautifulSoup)
        #
        response = requests.get(URLs[type] + str(pageNum))
        soup = BeautifulSoup(response.text, 'html.parser')
        return soup
        
    def __isEmpty(self, rawData: str) -> int:
        #
        # 가져온 Page의 공지 글 존재 여부 반환
        #
        # Parameter) 
        #   rawData: 공지 글의 존재 여부를 판단할 페이지 (Raw Data)
        #
        # Return: 공지 없으면 1 / 공지 존재하면 0 (Type: INT)
        #
        if (rawData.find(class_='empty_table') != None):
            return len(rawData.find(class_='empty_table'))
        else:
            return 0
        
    def __get_content_and_created_time_of_notice(self, url: str) -> str:
        #
        # 파라미터로 받은 공지글 내용과 작성 시간 가져오기
        #
        # Parameter)
        #   url: 가져올 공지사항의 URL
        #
        # Return) 공지사항의 내용 (Content; Type: STR) 및 작성 시간 (Created_time; Type: STR)
        #
        # Notice) 공지사항 페이지에 표시된 시간은 적절한 형태로 수정됩니다. (YY-DD-MM HH:MM -> YYYY-DD-MM HH:MM:00)
        #
        response = requests.get(url)
        soup = BeautifulSoup(response.text, 'html.parser')
        content = soup.select_one('#bo_v_con').get_text(strip=True).replace('\xa0', '')
        created_time = '20' + soup.select_one('.if_date').text.replace('작성일 ', '') + ':00' 
        return content, created_time
        
    
    def __parse_notice_of_each_page(self, type:str, pageNum: int, noticeCnt: int, noticeList: list) -> int:
        #
        # 가져온 Raw Data 파싱 -> 각 공지별 정보 추출하여 리스트에 저장
        # 하나의 페이지에 있는 공지를 파싱합니다.
        #
        # Parameter) 
        #   type: 가져와야 할 공지사항 종류 (공지사항 / 학부인재모집 / 취업정보)
        #   pageNum: 가져올 공지사항의 Page Number 
        #   noticeCnt: 한 페이지에서 가져올 공지사항의 수 -> 본 함수의 반환값에 따라 caller 함수에서 noticeCnt 값을 업데이트합니다.
        #               (크롤링한 공지 개수만큼 noticeCnt 값을 감소시킴; caller 함수는 callee 함수 (= This function) 를 반복 호출합니다.)
        #   noticeList: DB로 전송될 공지사항 객체 목록
        #               (공지사항 파싱 후, 객체를 append 합니다.)
        #
        # Return) 파싱한 공지사항 수 / -1: 공지사항 없음 (Empty Page) (Type: INT)
        #
        rawData = self.__get_raw_page_of_notice(type=type, pageNum=pageNum).select_one('tbody')
        
        if (self.__isEmpty(rawData=rawData) == 1):
            return -1
        
        rawData = rawData.find_all('tr')
        noticeCnt = MAX_COUNT_OF_NOTICE_PER_PAGE if (MAX_COUNT_OF_NOTICE_PER_PAGE < noticeCnt) else noticeCnt # 가져와야 할 공지가 페이지당 최대 공지 수보다 큰 경우
        noticeCnt = len(rawData) if (len(rawData) < noticeCnt) else noticeCnt # 가져와야 할 공지 수 > 페이지에 기록된 공지 수 (페이지에 공지가 가져와야 할 개수보다 부족)

        for i in range(noticeCnt): # 공지사항 정보를 추출합니다.
            noticeInfo = rawData[i].find('td', class_='td_subject') 
            
            title = noticeInfo.find('div', class_='bo_tit').get_text(strip=True) # 공지 제목 추출 및 양 끝 whiteSpace 제거
            link = re.sub("&page=[0-9]*", "", noticeInfo.find('div', class_='bo_tit').find('a')['href']) # 공지 링크 추출; 뒷부분 (&page={pageNum}) 삭제
            num = re.split("&wr_id=", link)[1] # 공지 URL에서 공지글 Number 추출
            if (type == '공지사항'):
                if (noticeInfo.find('a', class_='bo_cate_link').get_text(strip=True) == '대구형 계약학과[ICT융합학과]') :
                    category = CATEGORY_ALIAS['일반공지'] ## Temporary Fixed -> Need to handling!
                else:
                    category = CATEGORY_ALIAS[noticeInfo.find('a', class_='bo_cate_link').get_text(strip=True)] # 각 공지에 지정되어 있는 카테고리 추출
            else:
                category = type
            content, created_time = self.__get_content_and_created_time_of_notice(link) # 각 공지의 내용(Content) 및 작성 시간 (Created Time) 추출
            
            noticeObj = Notice(num=num, title=title, link=link, category=category, content=content, created_at=created_time) # 공지 객체 생성
            noticeList.append(noticeObj) #리스트에 공지 객체 추가
        
        return i + 1 # 크롤링한 공지 수 (생성된 공지 객체 수) 반환 (Type: INT)
    
    def get_all_notice(self, type: str, noticeCnt: int) -> list[Notice]:
        #
        # 공지사항을 noticeCnt 만큼 가져오는 함수
        # __parse_notice_of_each_page() 함수는 각 페이지에 있는 모든 공지를 가져옵니다. (MAX = 15)
        # __parse_notice_of_each_page() 함수를 반복 호출하여, noticeCnt 만큼 공지를 가져오면 됩니다.
        #
        # Parameter)
        #   type: 가져와야 할 공지사항 종류 (공지사항 / 학부인재모집 / 취업정보) 
        #   noticeCnt: 가져와야 할 공지사항의 수
        #
        # Return)
        #   DB로 전송될 공지사항 객체 목록 (Type: LIST[Notice])
        #
        # Notice) __parse_notice_of_each_page() 함수에 의해 공지사항 목록이 만들어집니다.
        #
        noticeList = list()
        pageNum = 1
        self.__get_max_count_of_notice_per_page(type=type) # 페이지당 최대 공지 수 업데이트
        
        while (noticeCnt): # 가져와야 할 공지사항이 남은 경우
            crawledCnt = self.__parse_notice_of_each_page(type=type, pageNum=pageNum, noticeCnt=noticeCnt, noticeList=noticeList) # 공지 가져오기 & 가져온 공지 수 반환
            
            if (crawledCnt == -1): # 페이지에 공지가 없는 경우 -> 가져올 수 있는 모든 공지를 가져온 상황
                break
            
            noticeCnt -= crawledCnt # 가져와야 할 공자사항 수에서 가져온 공지사항 수를 빼기
            pageNum += 1 # 페이지 갱신
            
        return noticeList
    
    def send_notice_to_api(self, BE_url: str, noticeList: list[Notice]) -> int:
        #
        # 가져온 공지사항을 Discord BackEnd 서버로 전송
        #
        # Parameter)
        #   BE_url: Discord BackEnd 서버 URL (SpringBoot)
        #   noticeList: 수집한 공지사항 목록
        #
        # Return) Discord BackEnd로부터 수신한 Status Code (Type: INT)
        #
        response = requests.post(
            BE_url, 
            json={'data': [notice.__dict__ for notice in noticeList]}, 
            headers={'Content-Type': 'application/json'}
            )

        return response
