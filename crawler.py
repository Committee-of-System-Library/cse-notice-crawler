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

link = None
title = None
category = None
createDate = None


def get_notice(searchCategory='전체', amount=1, *dataTypes):
    global link, title, category, createDate

    if searchCategory not in URLs:
        raise ValueError('category must be one of 전체, 일반공지, 학사, 장학, 심컴, 글솝, 대학원, 대학원 계약학과')
    
    elif set(dataTypes) - set(['link', 'title', 'category', 'createDate']):
        raise ValueError('data_type must be one of link, title, category, createDate')

    else:
        noticeList = []

        response = requests.get(URLs[searchCategory])
        soup = BeautifulSoup(response.text, 'html.parser')

        limit = int(soup.select_one('tbody tr:not(.bo_notice) td.td_num2').text.strip())

        if amount > limit:
            amount = limit

        if amount <= 15:
            searchList = list(soup.find('tbody').find_all('tr', class_=lambda x: x != 'bo_notice'))

            for idx in range(amount):
                link = searchList[idx].select('div.bo_tit a')[0].get('href')
                title = searchList[idx].select('div.bo_tit a')[0].text.strip()
                category = searchList[idx].select('td.td_subject a.bo_cate_link')[0].text if searchCategory == '전체' else searchCategory
                createDate = searchList[idx].find('td', class_='td_datetime hidden-xs').text

                if dataTypes == ():
                    noticeList.append([link, title, category, createDate])
                else:
                    noticeList.append([globals()[data] for data in dataTypes])

        else:
            pages = amount // 15 + 2

            for page in range(1, pages):
                response = requests.get(URLs[searchCategory] + '&page=' + str(page))
                soup = BeautifulSoup(response.text, 'html.parser')
                searchList = list(soup.find('tbody').find_all('tr', class_=lambda x: x != 'bo_notice'))

                if searchList == []:
                    break

                for idx in range(15 if page != pages - 1 else amount % 15):
                    link = searchList[idx].select('div.bo_tit a')[0].get('href')
                    title = searchList[idx].select('div.bo_tit a')[0].text.strip()
                    category = searchList[idx].select('td.td_subject a.bo_cate_link')[0].text if searchCategory == '전체' else searchCategory
                    createDate = searchList[idx].find('td', class_='td_datetime hidden-xs').text

                    if dataTypes == ():
                        noticeList.append([link, title, category, createDate])
                    else:
                        noticeList.append([globals()[data] for data in dataTypes])

        return noticeList

if __name__ == '__main__':
    noticeList = get_notice('전체', 55)
    print(len(noticeList))
    for notice in noticeList:
        print(notice)