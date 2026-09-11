from bs4 import BeautifulSoup

# 저장된 HTML 파일 읽기
with open('naver_page.html', 'r', encoding='utf-8') as f:
    html = f.read()

soup = BeautifulSoup(html, 'html.parser')

# 모든 'a' 태그 중에서 data-news-id가 있는 것 찾기
news_links = soup.find_all('a', attrs={'data-news-id': True})
print(f"data-news-id 속성이 있는 a 태그: {len(news_links)}")

if news_links:
    print("\n첫 3개 뉴스 링크:")
    for i, link in enumerate(news_links[:3]):
        print(f"\n[{i}]")
        print(f"  href: {link.get('href')}")
        print(f"  data-news-id: {link.get('data-news-id')}")
        print(f"  text: {link.get_text(strip=True)[:50]}")
        print(f"  전체 태그: {str(link)[:300]}")

# 다른 방법: 모든 li 중에서 data-newsid가 있는 것
print("\n\n=== data-newsid 속성 검색 ===")
newsid_items = soup.find_all(attrs={'data-newsid': True})
print(f"data-newsid 속성이 있는 요소: {len(newsid_items)}")

# 다른 방법: 클래스 이름으로 뉴스 아이템 찾기
print("\n\n=== 가능한 뉴스 컨테이너 ===")

# 모든 'li' 확인
all_li = soup.find_all('li')
print(f"전체 li 태그: {len(all_li)}")

# 'news' 관련 li 찾기
news_li = [li for li in all_li if li.get('class') and any('news' in str(c) for c in li.get('class', []))]
print(f"'news' 포함된 li: {len(news_li)}")

# data 속성이 있는 li 찾기
data_li = [li for li in all_li if li.get('data-news-id') or li.get('data-newsid') or li.get('data-news') or li.get('data-log')]
print(f"data 속성이 있는 li: {len(data_li)}")

if data_li:
    print("\n첫 번째 data 속성 li:")
    print(str(data_li[0])[:500])

# 다른 접근: 'group_news' div 찾기
print("\n\n=== group_news 확인 ===")
group_news = soup.find('div', class_='group_news')
if group_news:
    print("group_news 발견")
    # 내부의 모든 li 찾기
    inner_li = group_news.find_all('li', recursive=True)
    print(f"내부 li: {len(inner_li)}")
    
    # 직접 자식 li만
    direct_li = group_news.find_all('li', recursive=False)
    print(f"직접 자식 li: {len(direct_li)}")
    
    # 전체 내용 확인 (처음 1000자)
    print("\ngroup_news 전체 내용 (처음 1500자):")
    print(str(group_news)[:1500])

# JavaScript 데이터 찾기
print("\n\n=== 자바스크립트 데이터 검색 ===")
scripts = soup.find_all('script', type='application/ld+json')
print(f"application/ld+json 스크립트: {len(scripts)}")

if scripts:
    print("\n첫 번째 스크립트 내용 (처음 500자):")
    print(scripts[0].string[:500] if scripts[0].string else "없음")
