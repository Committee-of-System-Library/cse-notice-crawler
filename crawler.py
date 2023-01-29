import requests
from bs4 import BeautifulSoup

URLs = {
    '전체': 'https://computer.knu.ac.kr/bbs/board.php?bo_table=sub5_1',
    '일반공지': 'https://computer.knu.ac.kr/bbs/board.php?bo_table=sub5_1&sca=%EC%9D%BC%EB%B0%98%EA%B3%B5%EC%A7%80',
    '학사': 'https://computer.knu.ac.kr/bbs/board.php?bo_table=sub5_1&sca=%ED%95%99%EC%82%AC',
    '장학': 'https://computer.knu.ac.kr/bbs/board.php?bo_table=sub5_1&sca=%EC%9E%A5%ED%95%99',
    '심컴': 'https://computer.knu.ac.kr/bbs/board.php?bo_table=sub5_1&sca=%EC%8B%AC%EC%BB%B4',
    '글솝': 'https://computer.knu.ac.kr/bbs/board.php?bo_table=sub5_1&sca=%EA%B8%80%EC%86%9D',
    '대학원': 'https://computer.knu.ac.kr/bbs/board.php?bo_table=sub5_1&sca=%EB%8C%80%ED%95%99%EC%9B%90',
    '대학원 계약학과': 'https://computer.knu.ac.kr/bbs/board.php?bo_table=sub5_1&sca=%EB%8C%80%ED%95%99%EC%9B%90+%EA%B3%84%EC%95%BD%ED%95%99%EA%B3%BC'
}


def get_notice(category='전체', amount=1):
    notice_list = []

    if amount <= 15:
        response = requests.get(URLs[category])
        soup = BeautifulSoup(response.text, 'html.parser')
        
        link_list = list(soup.select('tr:not(.bo_notice) td div.bo_tit a'))

        for idx in range(amount):
            link = link_list[idx].get('href')
            title = link_list[idx].text.strip()

            response = requests.get(link)
            soup = BeautifulSoup(response.text, 'html.parser')
            category = soup.select_one('.bo_v_cate').text
            content = soup.select_one('#bo_v_con').text.strip().replace('\xa0', '')
            date = '20' + soup.select_one('.if_date').text.replace('작성일 ', '')

            notice_list.append((link, title, category, date, content))

    else:
        pages = amount // 15 + 2

        for page in range(1, pages):
            response = requests.get(URLs[category] + '&page=' + str(page))
            soup = BeautifulSoup(response.text, 'html.parser')

            link_list = list(soup.select('tr:not(.bo_notice) td div.bo_tit a'))

            if link_list == []:
                break

            for idx in range(15 if page != pages - 1 else amount % 15):
                link = link_list[idx].get('href')
                title = link_list[idx].text.strip()
    
                response = requests.get(link)
                soup = BeautifulSoup(response.text, 'html.parser')
                category = soup.select_one('.bo_v_cate').text
                content = soup.select_one('#bo_v_con').text.strip().replace('\xa0', '')
                date = '20' + soup.select_one('.if_date').text.replace('작성일 ', '')

                notice_list.append((link, title, category, date, content))

    return notice_list

if __name__ == '__main__':
    notice_list = get_notice('전체', 50)
    for notice in notice_list:
        print(notice[1])