import requests
from bs4 import BeautifulSoup
from openpyxl import Workbook
from openpyxl.styles import Font, Alignment
import time

def crawl_naver_news(search_query, num_pages=1):
    """
    네이버 뉴스 검색 결과를 크롤링
    
    Args:
        search_query: 검색어
        num_pages: 크롤링할 페이지 수
    
    Returns:
        기사 정보 리스트 (제목, URL, 언론사, 작성일)
    """
    articles = []
    
    for page in range(num_pages):
        # 네이버 뉴스 검색 URL
        start = page * 10
        url = f"https://search.naver.com/search.naver?where=news&query={search_query}&start={start}"
        
        try:
            # 헤더 설정 (봇 차단 방지)
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
            }
            response = requests.get(url, headers=headers, timeout=10)
            response.encoding = 'utf-8'
            
            if response.status_code == 200:
                soup = BeautifulSoup(response.content, 'html.parser')
                
                # 각 기사 항목 찾기
                article_items = soup.find_all('div', class_='VPvIMtQGxcVp0yk5')
                
                for item in article_items:
                    try:
                        # 제목과 URL 추출
                        title_link = item.find('a', class_='fSjI1YZLZceoACwh')
                        if not title_link:
                            title_link = item.find('a', {'data-nlog-area': 'nws_all.h.tit'})
                        
                        if title_link:
                            title_elem = title_link.find('span', class_='sds-comps-text-type-headline1')
                            if title_elem:
                                title = title_elem.get_text(strip=True)
                            else:
                                title_spans = title_link.find_all('span')
                                title = ' '.join([s.get_text(strip=True) for s in title_spans if s.get_text(strip=True)])
                            
                            article_url = title_link.get('href', '')
                        else:
                            continue
                        
                        # 언론사 추출
                        press_elem = item.find('span', class_='sds-comps-profile-info-title-text')
                        if press_elem:
                            press_link = press_elem.find('a')
                            if press_link:
                                press = press_link.get_text(strip=True)
                            else:
                                press = press_elem.get_text(strip=True)
                        else:
                            press = 'N/A'
                        
                        # "새 창 열림" 텍스트 제거
                        press = press.replace('새 창 열림', '').strip()
                        
                        # 작성일 추출
                        date_elem = None
                        # profile-info-subtexts 내에서 시간 정보 찾기
                        subtexts = item.find('div', class_='sds-comps-horizontal-layout sds-comps-inline-layout sds-comps-profile-info-subtexts')
                        if subtexts:
                            # 모든 span 태그 찾기
                            spans = subtexts.find_all('span', class_='sds-comps-text-ellipsis-1')
                            if spans:
                                # 첫 번째 시간 정보 (보통 가장 먼저 나타남)
                                publish_date = spans[0].get_text(strip=True)
                            else:
                                # 다른 방법으로 찾기
                                time_info = subtexts.find('span', string=lambda x: x and ('전' in x or '시' in x or '분' in x))
                                if time_info:
                                    publish_date = time_info.get_text(strip=True)
                                else:
                                    publish_date = 'N/A'
                        else:
                            publish_date = 'N/A'
                        
                        # 기사 정보 저장
                        article_info = {
                            '제목': title,
                            'URL': article_url,
                            '언론사': press,
                            '작성일': publish_date
                        }
                        articles.append(article_info)
                        
                    except Exception as e:
                        print(f"기사 파싱 오류: {e}")
                        continue
                
                print(f"페이지 {page + 1}: {len(article_items)}개 기사 크롤링 완료")
                
            else:
                print(f"페이지 {page + 1} 요청 실패: {response.status_code}")
            
            # 요청 간격 설정 (서버 부하 방지)
            time.sleep(1)
            
        except Exception as e:
            print(f"페이지 {page + 1} 크롤링 오류: {e}")
            continue
    
    return articles


def save_to_excel(articles, filename='naverResult.xlsx'):
    """
    크롤링한 기사 정보를 Excel 파일로 저장
    
    Args:
        articles: 기사 정보 리스트
        filename: 저장할 파일명
    """
    # Workbook 생성
    wb = Workbook()
    ws = wb.active
    ws.title = '뉴스'
    
    # 헤더 설정
    headers = ['번호', '제목', 'URL', '언론사', '작성일']
    ws.append(headers)
    
    # 헤더 스타일 (굵게, 정렬)
    for cell in ws[1]:
        cell.font = Font(bold=True)
        cell.alignment = Alignment(horizontal='center', vertical='center')
    
    # 데이터 입력
    for idx, article in enumerate(articles, 1):
        ws.append([
            idx,
            article['제목'],
            article['URL'],
            article['언론사'],
            article['작성일']
        ])
    
    # 열 너비 자동 조정
    ws.column_dimensions['A'].width = 8
    ws.column_dimensions['B'].width = 50
    ws.column_dimensions['C'].width = 50
    ws.column_dimensions['D'].width = 15
    ws.column_dimensions['E'].width = 15
    
    # 셀 정렬
    for row in ws.iter_rows(min_row=2, max_row=ws.max_row):
        row[0].alignment = Alignment(horizontal='center')
        row[2].alignment = Alignment(horizontal='left', wrap_text=True)
        row[3].alignment = Alignment(horizontal='center')
        row[4].alignment = Alignment(horizontal='center')
    
    # 파일 저장
    wb.save(filename)
    print(f"\n✓ '{filename}' 파일로 {len(articles)}개 기사가 저장되었습니다.")


if __name__ == '__main__':
    # 검색어 설정
    search_query = '반도체'
    
    # 뉴스 크롤링
    print(f"'{search_query}' 관련 뉴스를 크롤링 중입니다...\n")
    articles = crawl_naver_news(search_query, num_pages=1)
    
    # 결과 출력
    print(f"\n총 {len(articles)}개의 기사를 크롤링했습니다.\n")
    for idx, article in enumerate(articles, 1):
        print(f"[{idx}] {article['제목']}")
        print(f"    언론사: {article['언론사']} | 작성일: {article['작성일']}")
        print(f"    URL: {article['URL']}\n")
    
    # Excel 파일로 저장
    save_to_excel(articles, 'naverResult.xlsx')
