from selenium import webdriver
from selenium.webdriver.common.by import By
import time

# Chrome 드라이버 설정
options = webdriver.ChromeOptions()
options.add_argument('--disable-blink-features=AutomationControlled')
options.add_argument('user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36')

driver = webdriver.Chrome(options=options)

try:
    url = "https://search.naver.com/search.naver?where=news&sm=tab_jum&query=반도체&start=1"
    driver.get(url)
    time.sleep(3)  # 페이지 로드 대기
    
    # 전체 HTML 저장
    html = driver.page_source
    
    with open('naver_page.html', 'w', encoding='utf-8') as f:
        f.write(html)
    
    print("HTML 파일 저장 완료: naver_page.html")
    
    # 콘솔에도 일부 출력
    print(f"\n총 HTML 길이: {len(html)} 바이트")
    
    # 특정 텍스트 검색
    if '반도체' in html:
        print("'반도체' 텍스트 포함됨")
    
    # 뉴스 관련 마크업 찾기
    from bs4 import BeautifulSoup
    soup = BeautifulSoup(html, 'html.parser')
    
    # 모든 div 중에서 'news'가 포함된 것
    all_elements = soup.find_all(True)
    news_related = [e for e in all_elements if str(e.get('class', [])).lower().find('news') > -1 or str(e.get('id', '')).lower().find('news') > -1]
    
    print(f"\n'news' 관련 요소: {len(news_related)}")
    
    # li 태그 확인
    all_lis = soup.find_all('li')
    print(f"전체 li 태그: {len(all_lis)}")
    
    # 첫 10개 li 클래스 출력
    print("\n첫 10개 li 태그:")
    for i, li in enumerate(all_lis[:10]):
        classes = li.get('class', [])
        print(f"  [{i}] class={classes}, text={li.get_text(strip=True)[:50]}")

finally:
    driver.quit()
