import requests
from bs4 import BeautifulSoup
import json

url = "https://search.naver.com/search.naver?where=news&sm=tab_jum&query=반도체&start=1"

headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
}

response = requests.get(url, headers=headers)
response.encoding = 'utf-8'
soup = BeautifulSoup(response.text, 'html.parser')

# group_news 클래스 찾기
news_groups = soup.find_all('div', class_='group_news')
print(f"group_news 발견: {len(news_groups)}")

if news_groups:
    # 첫 번째 그룹 내용 확인
    print("\n=== 첫 번째 group_news 내부 구조 ===")
    first_group = news_groups[0]
    
    # 모든 li 태그 찾기
    all_lis = first_group.find_all('li')
    print(f"li 태그 개수: {len(all_lis)}")
    
    if all_lis:
        # 첫 번째 li의 전체 HTML 출력
        print("\n첫 번째 li 태그 (처음 1500자):")
        print(str(all_lis[0])[:1500])
        
        # 첫 번째 li 내에서 찾을 수 있는 요소들
        first_li = all_lis[0]
        print("\n=== 첫 번째 li에서 찾을 수 있는 요소들 ===")
        
        # a 태그 찾기
        all_a_tags = first_li.find_all('a')
        print(f"a 태그: {len(all_a_tags)}")
        for i, a in enumerate(all_a_tags):
            print(f"  [{i}] href={a.get('href')}, text={a.get_text(strip=True)[:50]}")
        
        # 모든 클래스 찾기
        all_tags = first_li.find_all(True)
        classes = set()
        for tag in all_tags:
            if tag.get('class'):
                classes.add(' '.join(tag.get('class')))
        
        print("\n발견된 클래스들:")
        for cls in sorted(classes):
            print(f"  - {cls}")

# 다른 가능한 선택자들
print("\n\n=== 다른 선택자 시도 ===")
print(f"article 태그: {len(soup.find_all('article'))}")
print(f"li.bx: {len(soup.find_all('li', class_='bx'))}")

# li.bx 내용 확인
bx_items = soup.find_all('li', class_='bx')
if bx_items:
    print("\n첫 번째 li.bx 내용:")
    print(str(bx_items[0])[:800])
