from pprint import pprint
import random

import requests
import time
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.common import NoSuchElementException
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager


def crawler_daum_news():
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)AppleWebKit/537.36 (KHTML, like Gecko) Chrome/73.0.3683.86 Safari/537.36'
    }
    url = 'https://news.daum.net'

    options = webdriver.ChromeOptions()
    options.add_argument('--no-sandbox')
    options.add_argument('--disable-dev-shm-usage')
    options.add_argument("user-agent=Mozilla/5.0 (Windows NT 6.1; WOW64; Trident/7.0; rv:11.0) like Gecko")
    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)

    data = requests.get(url, headers=headers)
    soup = BeautifulSoup(data.text, 'html.parser')
    news_issue = soup.select_one('.list_newsissue')
    news_list = news_issue.select('.item_issue')
    for news in news_list:
        detail_url = news.select_one('a')['href']
        title = news.select_one('.cont_thumb > .tit_g').text.strip()
        # print(f"url = {detail_url}, title = {title}")
        driver.get(detail_url)
        time.sleep(0.5)

        # 댓글창 확인
        try:
            cmt_toggle = driver.find_element(By.CLASS_NAME, 'img_cmt.ico_fold')
            cmt_toggle.click()
            time.sleep(1)
            cmt_content_path = driver.find_element(By.CLASS_NAME, 'desc_txt.font_size_')
        except NoSuchElementException:
            continue
        cmt_contents = []

        cmt_content = ''
        if cmt_content_path:
            cmt_content = cmt_content_path.text.strip()
        cmt_contents.append(cmt_content)

        doc = {
            'title': title,
            'detail_url': detail_url,
            'cmt_contents': cmt_contents
        }

        pprint(doc)


def crawler_everytime(ev_id, ev_pw):
    if not ev_id or not ev_pw:
        print('Error! id와 pw는 필수 값입니다.')
        return

    url = 'https://everytime.kr/'

    options = webdriver.ChromeOptions()
    options.add_argument('--no-sandbox')
    options.add_argument('--disable-dev-shm-usage')
    options.add_argument("user-agent=Mozilla/5.0 (Windows NT 6.1; WOW64; Trident/7.0; rv:11.0) like Gecko")
    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)

    # 0. 에브리타임 접속
    driver.get(url)

    # 1. 로그인
    driver.find_element(By.CLASS_NAME, 'button.login').click()
    time.sleep(random.uniform(0.5, 1))
    input_id = driver.find_element(By.XPATH, "//p[@class='input']/input[@type='text']")
    input_pw = driver.find_element(By.XPATH, "//p[@class='input']/input[@type='password']")
    input_id.send_keys(ev_id)
    input_pw.send_keys(ev_pw)
    time.sleep(random.uniform(0.5, 0.7))
    driver.find_element(By.XPATH, '//input[@type="submit"]').click()

    # 2. 자유게시판 이동
    driver.find_element(By.CLASS_NAME, 'new').click()
    time.sleep(random.uniform(1, 2))

    # 3. 게시글 목록 가져오기 (url)
    article_list = driver.find_elements(By.TAG_NAME, 'article')
    article_url_list = []
    for article in article_list:
        ev_url = article.find_element(By.TAG_NAME, 'a').get_attribute('href')
        ev_comment_cnt = article.find_element(By.CLASS_NAME, 'comment').text
        if int(ev_comment_cnt) > 0:  # 댓글이 있는 게시글만
            article_url_list.append(ev_url)

    # 4. 게시글 상세 페이지 이동
    article_cnt = 0
    for article_url in article_url_list:
        driver.get(article_url)
        time.sleep(0.5)
        try:
            # 제목, 내용, 시간
            ev_title = driver.find_element(By.XPATH, "//article/a/h2[@class='large']").text
            ev_content = driver.find_element(By.XPATH, "//article/a/p[@class='large']").text
            ev_time = driver.find_element(By.XPATH, "//article/a/div/time[@class='large']").text
            # 공감수, 스크랩수
            status = driver.find_element(By.XPATH, '//article/a/ul[@class="status left"]')
            ev_vote_cnt = status.find_element(By.CLASS_NAME, 'vote').text
            ev_scrap_cnt = status.find_element(By.CLASS_NAME, 'scrap').text
            # 댓글
            comment_list = driver.find_elements(By.CLASS_NAME, 'comments')
        except NoSuchElementException:
            print('Warn! 게시물 정보 추출 실패!')
            continue
        ev_comments = []
        ev_comment_frame = {
            'comment_user': '',
            'comment_content': '',
            'comment_time': ''
        }
        for comment in comment_list:
            try:
                ev_comment_frame['comment_user'] = comment.find_element(By.TAG_NAME, 'h3').text
                ev_comment_frame['comment_content'] = comment.find_element(By.TAG_NAME, 'p').text
                ev_comment_frame['comment_time'] = comment.find_element(By.TAG_NAME, 'time').text
                ev_comments.append(ev_comment_frame)
            except NoSuchElementException:
                print('Warn! 댓글 추출 실패')
                continue

        article_cnt += 1
        print(f"{article_cnt}. ev_url = {ev_url}, ev_title = {ev_title}, ev_content = {ev_content}, ev_time = {ev_time}, ev_vote_cnt = {ev_vote_cnt}, ev_scrap_cnt = {ev_scrap_cnt}, ev_comments = {ev_comments}")


if __name__ == "__main__":
    import config
    # 다음 뉴스 크롤러
    # crawler_daum_news()

    # 에브리타임 크롤러
    everytime_id = config.ev_account.get('id')
    everytime_pw = config.ev_account.get('pw')
    crawler_everytime(everytime_id, everytime_pw)
