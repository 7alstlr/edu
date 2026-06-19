import requests
from bs4 import BeautifulSoup
import pandas as pd
from datetime import datetime
import time

# 홈앤쇼핑 편성표 크롤링
def crawl_hnsmall_schedule():
    """
    홈앤쇼핑 TV 편성표 크롤링
    """
    try:
        print("[1/3] 홈쇼핑모아 편성표 페이지 요청 중...")

        # 홈쇼핑모아 URL (모든 홈쇼핑 통합)
        url = "https://hsmoa.com/"

        # 헤더 설정 (User-Agent)
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        }

        # 요청 (SSL 검증 비활성화)
        response = requests.get(url, headers=headers, timeout=10, verify=False)
        response.encoding = 'utf-8'

        if response.status_code != 200:
            print(f"ERROR: HTTP {response.status_code}")
            return None

        print("[2/3] HTML 파싱 중...")
        soup = BeautifulSoup(response.content, 'html.parser')

        # 편성표 데이터 추출
        print("[3/3] 데이터 추출 중...")

        # 편성표 테이블 찾기
        schedule_data = []

        # 페이지 구조에 따라 수정 필요
        # 임시: 페이지 텍스트 출력으로 구조 확인
        print("\n=== 페이지 제목 ===")
        title = soup.find('title')
        if title:
            print(f"Title: {title.text}")

        print("\n=== 메인 콘텐츠 ===")
        main_content = soup.find('div', class_=['container', 'main', 'content'])
        if main_content:
            text_content = main_content.get_text()[:500]
            print(text_content)
        else:
            # 다른 클래스명으로 시도
            print("메인 콘텐츠를 찾지 못했습니다.")
            print("페이지의 div 요소들:")
            divs = soup.find_all('div', limit=5)
            for i, div in enumerate(divs):
                print(f"  {i}: {div.get('class')}")

        print("\n크롤링 완료!")
        return schedule_data

    except requests.exceptions.RequestException as e:
        print(f"ERROR: 요청 실패 - {str(e)}")
        return None
    except Exception as e:
        print(f"ERROR: {str(e)}")
        return None

if __name__ == "__main__":
    print("홈앤쇼핑 편성표 크롤링 시작\n")
    crawl_hnsmall_schedule()
