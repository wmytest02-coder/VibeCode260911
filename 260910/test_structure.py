import requests
from bs4 import BeautifulSoup

url = 'https://finance.naver.com/sise/sise_index.naver?code=KPI200'
headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'}

response = requests.get(url, headers=headers)
response.encoding = 'utf-8'

# 원본 HTML에서 "편입종목상위" 포함된 부분 찾기
if '편입종목상위' in response.text:
    print("찾음: 편입종목상위")
    # 해당 텍스트 주변 부분 출력
    idx = response.text.find('편입종목상위')
    print("---주변 HTML---")
    print(response.text[max(0, idx-300):idx+300])
else:
    print("찾지 못함: 편입종목상위")
    
# 모든 테이블 개수 확인
soup = BeautifulSoup(response.content, 'html.parser')
tables = soup.find_all('table')
print(f"\n테이블 개수: {len(tables)}")

# 각 테이블의 행 개수 출력
for i, table in enumerate(tables):
    thead = table.find('thead')
    tbody = table.find('tbody')
    if thead:
        headers_list = [th.get_text(strip=True) for th in thead.find_all('th')[:5]]
        rows = tbody.find_all('tr') if tbody else []
        if '현재가' in str(headers_list) or '거래' in str(headers_list):
            print(f"\n테이블 {i}: 헤더={headers_list}, 행={len(rows)}")
            # 첫 2개 행 출력
            for j, row in enumerate(rows[:2]):
                cols = [td.get_text(strip=True) for td in row.find_all('td')[:5]]
                print(f"  행 {j}: {cols}")
