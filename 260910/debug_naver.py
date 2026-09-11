import requests
from bs4 import BeautifulSoup

# 실제 페이지 구조 확인용 디버깅 코드
url = "https://search.naver.com/search.naver?where=news&sm=tab_jum&query=반도체&start=1"

headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
}

print("페이지 요청 중...")
response = requests.get(url, headers=headers)
response.encoding = 'utf-8'

print(f"상태 코드: {response.status_code}")
print(f"\n HTML 길이: {len(response.text)} 바이트")

soup = BeautifulSoup(response.text, 'html.parser')

# 다양한 선택자로 시도
print("\n=== CSS 클래스별 검색 ===")

# 기존 선택자
print(f"div.news_area: {len(soup.find_all('div', class_='news_area'))}")

# 다른 가능한 클래스들
print(f"div.news-area: {len(soup.find_all('div', class_='news-area'))}")
print(f"li.bx: {len(soup.find_all('li', class_='bx'))}")
print(f"article: {len(soup.find_all('article'))}")

# 전체 div 중 news 관련 클래스 찾기
all_divs = soup.find_all('div')
news_related = [div for div in all_divs if div.get('class') and 'news' in ' '.join(div.get('class', []))]
print(f"\n'news' 포함된 div 클래스: {len(news_related)}")
if news_related:
    for div in news_related[:3]:
        print(f"  - {div.get('class')}")

# 전체 li 태그 확인
all_lis = soup.find_all('li')
print(f"\n전체 li 태그: {len(all_lis)}")

# 전체 구조 중 일부 출력
print("\n=== 페이지 내용 일부 (처음 3000자) ===")
print(response.text[:3000])
