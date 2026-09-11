import requests
from bs4 import BeautifulSoup
import pandas as pd
import re

def extract_text_clean(td_element):
    """
    td 요소에서 텍스트 추출 (공백 및 개행 정리)
    """
    text = td_element.get_text(strip=True)
    # 여러 개의 공백을 하나로 통일
    text = re.sub(r'\s+', ' ', text)
    return text.strip()

def extract_previous_day(td_element):
    """
    전일비 추출 - 상승/하락 텍스트와 숫자를 정확하게 추출
    """
    # blind 클래스의 span에서 상승/하락 텍스트 추출
    blind_span = td_element.find('span', class_='blind')
    direction = blind_span.get_text(strip=True) if blind_span else ''
    
    # 숫자 span 찾기
    span_with_number = td_element.find('span', class_='tah')
    if span_with_number:
        number = span_with_number.get_text(strip=True)
        return f"{direction}{number}" if direction else number
    
    return extract_text_clean(td_element)

def crawl_kospi200_stocks():
    """
    네이버 금융에서 KOSPI 200 편입종목상위 정보를 크롤링하는 함수
    BeautifulSoup을 사용하여 HTML 파싱
    """
    url = "https://finance.naver.com/sise/entryJongmok.naver?type=KPI200"
    
    try:
        # User-Agent 및 헤더 설정
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Referer': 'https://finance.naver.com/',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'ko-KR,ko;q=0.9',
        }
        
        # 웹페이지 요청
        print(f"페이지 접속 중: {url}")
        response = requests.get(url, headers=headers, timeout=15)
        response.encoding = 'utf-8'
        
        if response.status_code != 200:
            print(f"요청 실패: 상태 코드 {response.status_code}")
            return None
        
        # BeautifulSoup 파싱
        soup = BeautifulSoup(response.content, 'html.parser')
        
        stocks_data = []
        
        # "편입종목상위" 테이블 찾기
        # h4 태그에서 "편입종목상위" 찾기
        h4_tag = soup.find('h4', class_='top_tlt')
        if not h4_tag or '편입종목상위' not in h4_tag.get_text():
            print("편입종목상위 섹션을 찾을 수 없습니다.")
            return None
        
        # 다음 테이블 찾기
        table = h4_tag.find_next('table', class_='type_1')
        if not table:
            print("테이블을 찾을 수 없습니다.")
            return None
        
        print("✓ 편입종목상위 테이블을 찾았습니다.")
        
        # tbody 또는 직접 tr 찾기
        tbody = table.find('tbody')
        if not tbody:
            # tbody가 없으면 table의 직접 자식 tr들 찾기
            rows = table.find_all('tr', recursive=False)
        else:
            rows = tbody.find_all('tr')
        
        if not rows:
            print("행을 찾을 수 없습니다.")
            return None
        
        print(f"찾은 행 개수: {len(rows)}")
        
        data_started = False
        
        for row_idx, row in enumerate(rows):
            # blank_07, blank_09, division_line 행 제외
            if row.get('class'):
                classes = ' '.join(row.get('class', []))
                if 'blank' in classes or 'division_line' in classes:
                    continue
            
            cols = row.find_all('td')
            
            # 최소 7개 컬럼이 필요
            if len(cols) < 7:
                continue
            
            try:
                # 첫 번째 컬럼 (종목명) 추출
                col0 = cols[0]
                link = col0.find('a')
                
                if link:
                    stock_name = link.get_text(strip=True)
                else:
                    stock_name = extract_text_clean(col0)
                
                # 종목명 유효성 검사
                if not stock_name or len(stock_name) == 0:
                    continue
                
                # 종목명이 숫자만 있거나 너무 긴 경우 제외
                if stock_name.replace(',', '').replace('%', '').replace('-', '').replace('+', '').isdigit():
                    continue
                
                # 각 컬럼 데이터 추출
                current_price = extract_text_clean(cols[1])
                previous_day = extract_previous_day(cols[2])
                change_rate = extract_text_clean(cols[3])
                trading_volume = extract_text_clean(cols[4])
                trading_amount = extract_text_clean(cols[5])
                market_cap = extract_text_clean(cols[6])
                
                # 현재가에 숫자가 있는지 확인 (데이터 유효성)
                if not any(c.isdigit() for c in current_price):
                    continue
                
                stock_info = {
                    '종목명': stock_name,
                    '현재가': current_price,
                    '전일비': previous_day,
                    '등락률': change_rate,
                    '거래량': trading_volume,
                    '거래대금(백만)': trading_amount,
                    '시가총액(억)': market_cap
                }
                stocks_data.append(stock_info)
                data_started = True
                
                if len(stocks_data) <= 3:
                    print(f"  추출 {len(stocks_data)}: {stock_name} - {current_price}")
            
            except Exception as e:
                if data_started:  # 데이터 추출이 시작된 후 오류는 무시
                    pass
                else:
                    raise
        
        # 결과 처리
        if stocks_data:
            print(f"\n✓ 수집된 종목 수: {len(stocks_data)}")
            print("\n" + "=" * 140)
            
            # DataFrame으로 변환
            df = pd.DataFrame(stocks_data)
            print(df.to_string(index=False))
            print("=" * 140)
            
            return df
        else:
            print("\n⚠ 종목 데이터를 추출하지 못했습니다.")
            return None
    
    except requests.exceptions.Timeout:
        print("요청 시간 초과 - 네트워크 연결을 확인하세요")
        return None
    except requests.exceptions.RequestException as e:
        print(f"웹 요청 중 오류: {e}")
        return None
    except Exception as e:
        print(f"크롤링 중 오류 발생: {e}")
        import traceback
        traceback.print_exc()
        return None


def save_to_csv(df, filename='kospi200_stocks.csv'):
    """
    크롤링된 데이터를 CSV 파일로 저장
    """
    if df is not None and len(df) > 0:
        df.to_csv(filename, index=False, encoding='utf-8-sig')
        print(f"✓ 데이터가 '{filename}'으로 저장되었습니다.")
        return True
    else:
        print("⚠ 저장할 데이터가 없습니다.")
        return False


if __name__ == "__main__":
    print("=" * 130)
    print("KOSPI 200 편입종목상위 정보 크롤링 시작...")
    print("=" * 130 + "\n")
    
    # 크롤링 수행
    stocks_df = crawl_kospi200_stocks()
    
    # 데이터 저장
    if stocks_df is not None and len(stocks_df) > 0:
        save_to_csv(stocks_df, 'kospi200_stocks.csv')
        print("\n✓ 크롤링이 완료되었습니다!")
    else:
        print("\n⚠ 크롤링 실패 - 다시 시도해주세요.")
