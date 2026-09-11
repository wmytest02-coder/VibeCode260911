from bs4 import BeautifulSoup

with open('naver_page.html', 'r', encoding='utf-8') as f:
    html = f.read()

soup = BeautifulSoup(html, 'html.parser')

# list_news 클래스 찾기
list_news = soup.find('ul', class_='list_news')
if list_news:
    print("list_news 발견")
    
    # 직접 자식 요소 확인
    children = list(list_news.children)
    print(f"직접 자식 요소: {len(children)}")
    
    # 텍스트 노드 제외한 실제 요소
    elements = [child for child in children if hasattr(child, 'name')]
    print(f"실제 요소: {len(elements)}")
    
    # 첫 몇 개 요소 타입 확인
    print("\n첫 10개 요소:")
    for i, elem in enumerate(elements[:10]):
        if hasattr(elem, 'get'):
            print(f"  [{i}] tag={elem.name}, class={elem.get('class')}, text={elem.get_text(strip=True)[:50]}")
        else:
            print(f"  [{i}] type={type(elem).__name__}, content={str(elem)[:50]}")
    
    # 모든 'a' 태그 찾기
    all_a = list_news.find_all('a', limit=20)
    print(f"\n처음 20개 a 태그:")
    for i, a in enumerate(all_a):
        href = a.get('href', '')
        text = a.get_text(strip=True)
        parent_tag = a.parent.name if a.parent else 'None'
        print(f"  [{i}] href={href[:50] if href else 'None'}, text={text[:50]}, parent={parent_tag}")
        
        # news 관련 URL 확인
        if 'news' in href or 'article' in href or '.com' in href:
            print(f"      >> 이것이 기사 링크일 수 있음!")

# 다른 접근: 모든 텍스트 노드에서 기사 찾기
print("\n\n=== 페이지 전체에서 뉴스 기사 찾기 ===")

# 페이지의 주요 내용 구역 찾기
main_content = soup.find('div', class_='group_news')
if main_content:
    # 모든 a 태그 중에서 외부 링크 찾기
    external_links = []
    for a in main_content.find_all('a'):
        href = a.get('href', '')
        if href.startswith('http') and 'naver' not in href:
            external_links.append({
                'url': href,
                'text': a.get_text(strip=True),
                'tag': str(a)[:200]
            })
    
    print(f"\n외부 링크 (뉴스 기사): {len(external_links)}")
    for i, link in enumerate(external_links[:5]):
        print(f"\n[{i}]")
        print(f"  Text: {link['text'][:60]}")
        print(f"  URL: {link['url'][:80]}")
