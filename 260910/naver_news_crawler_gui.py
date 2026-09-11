import sys
import requests
from bs4 import BeautifulSoup
from openpyxl import Workbook
from openpyxl.styles import Font, Alignment
from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QLabel, QLineEdit, QSpinBox, QPushButton, QTableWidget, QTableWidgetItem,
    QTextEdit, QFileDialog, QMessageBox, QProgressBar
)
from PyQt6.QtCore import QThread, pyqtSignal, Qt
from PyQt6.QtGui import QFont
import time


class CrawlerThread(QThread):
    """뉴스 크롤링을 별도 스레드에서 처리"""
    progress_updated = pyqtSignal(str)
    data_ready = pyqtSignal(list)
    finished = pyqtSignal()
    error_occurred = pyqtSignal(str)
    
    def __init__(self, search_query, num_pages):
        super().__init__()
        self.search_query = search_query
        self.num_pages = num_pages
        self.articles = []
    
    def run(self):
        try:
            self.articles = self.crawl_naver_news()
            self.data_ready.emit(self.articles)
            self.finished.emit()
        except Exception as e:
            self.error_occurred.emit(f"크롤링 오류: {str(e)}")
    
    def crawl_naver_news(self):
        """네이버 뉴스 검색 결과를 크롤링"""
        articles = []
        
        for page in range(self.num_pages):
            self.progress_updated.emit(f"페이지 {page + 1}/{self.num_pages} 크롤링 중...")
            
            start = page * 10
            url = f"https://search.naver.com/search.naver?where=news&query={self.search_query}&start={start}"
            
            try:
                headers = {
                    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
                }
                response = requests.get(url, headers=headers, timeout=10)
                response.encoding = 'utf-8'
                
                if response.status_code == 200:
                    soup = BeautifulSoup(response.content, 'html.parser')
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
                            
                            press = press.replace('새 창 열림', '').strip()
                            
                            # 작성일 추출
                            subtexts = item.find('div', class_='sds-comps-horizontal-layout sds-comps-inline-layout sds-comps-profile-info-subtexts')
                            if subtexts:
                                spans = subtexts.find_all('span', class_='sds-comps-text-ellipsis-1')
                                if spans:
                                    publish_date = spans[0].get_text(strip=True)
                                else:
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
                            continue
                    
                    self.progress_updated.emit(f"페이지 {page + 1}: {len(article_items)}개 기사 크롤링 완료")
                
                else:
                    self.progress_updated.emit(f"페이지 {page + 1} 요청 실패: {response.status_code}")
                
                time.sleep(1)
                
            except Exception as e:
                self.progress_updated.emit(f"페이지 {page + 1} 크롤링 오류: {str(e)}")
        
        return articles


class NaverNewsCrawlerGUI(QMainWindow):
    """네이버 뉴스 크롤러 GUI 애플리케이션"""
    
    def __init__(self):
        super().__init__()
        self.crawler_thread = None
        self.articles = []
        self.init_ui()
    
    def init_ui(self):
        """UI 초기화"""
        self.setWindowTitle('네이버 뉴스 크롤러 - PyQt6')
        self.setGeometry(100, 100, 1200, 800)
        
        # 중앙 위젯 설정
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QVBoxLayout()
        
        # ===== 상단: 검색 설정 영역 =====
        search_layout = QHBoxLayout()
        
        # 검색어 입력
        search_label = QLabel('검색어:')
        search_label.setFont(QFont('Arial', 10))
        self.search_input = QLineEdit()
        self.search_input.setText('반도체')
        self.search_input.setPlaceholderText('검색할 키워드를 입력하세요')
        
        # 페이지 수 입력
        page_label = QLabel('페이지 수:')
        page_label.setFont(QFont('Arial', 10))
        self.page_spinbox = QSpinBox()
        self.page_spinbox.setMinimum(1)
        self.page_spinbox.setMaximum(10)
        self.page_spinbox.setValue(1)
        
        # 크롤링 시작 버튼
        self.crawl_button = QPushButton('크롤링 시작')
        self.crawl_button.clicked.connect(self.start_crawling)
        self.crawl_button.setFixedWidth(120)
        
        # 저장 버튼
        self.save_button = QPushButton('Excel로 저장')
        self.save_button.clicked.connect(self.save_to_excel)
        self.save_button.setFixedWidth(120)
        self.save_button.setEnabled(False)
        
        search_layout.addWidget(search_label)
        search_layout.addWidget(self.search_input)
        search_layout.addWidget(page_label)
        search_layout.addWidget(self.page_spinbox)
        search_layout.addWidget(self.crawl_button)
        search_layout.addWidget(self.save_button)
        search_layout.addStretch()
        
        main_layout.addLayout(search_layout)
        
        # ===== 중간: 진행 상황 =====
        progress_label = QLabel('진행 상황:')
        progress_label.setFont(QFont('Arial', 10, QFont.Weight.Bold))
        main_layout.addWidget(progress_label)
        
        self.progress_text = QTextEdit()
        self.progress_text.setReadOnly(True)
        self.progress_text.setFixedHeight(100)
        main_layout.addWidget(self.progress_text)
        
        self.progress_bar = QProgressBar()
        self.progress_bar.setFixedHeight(20)
        main_layout.addWidget(self.progress_bar)
        
        # ===== 하단: 결과 테이블 =====
        result_label = QLabel('크롤링 결과:')
        result_label.setFont(QFont('Arial', 10, QFont.Weight.Bold))
        main_layout.addWidget(result_label)
        
        self.result_table = QTableWidget()
        self.result_table.setColumnCount(5)
        self.result_table.setHorizontalHeaderLabels(['번호', '제목', 'URL', '언론사', '작성일'])
        self.result_table.setColumnWidth(0, 50)
        self.result_table.setColumnWidth(1, 400)
        self.result_table.setColumnWidth(2, 300)
        self.result_table.setColumnWidth(3, 100)
        self.result_table.setColumnWidth(4, 100)
        main_layout.addWidget(self.result_table)
        
        central_widget.setLayout(main_layout)
    
    def start_crawling(self):
        """크롤링 시작"""
        search_query = self.search_input.text().strip()
        num_pages = self.page_spinbox.value()
        
        if not search_query:
            QMessageBox.warning(self, '입력 오류', '검색어를 입력해주세요.')
            return
        
        # UI 업데이트
        self.crawl_button.setEnabled(False)
        self.save_button.setEnabled(False)
        self.progress_text.clear()
        self.result_table.setRowCount(0)
        self.articles = []
        
        # 크롤러 스레드 생성 및 시작
        self.crawler_thread = CrawlerThread(search_query, num_pages)
        self.crawler_thread.progress_updated.connect(self.update_progress)
        self.crawler_thread.data_ready.connect(self.display_results)
        self.crawler_thread.finished.connect(self.crawling_finished)
        self.crawler_thread.error_occurred.connect(self.show_error)
        
        self.crawler_thread.start()
    
    def update_progress(self, message):
        """진행 상황 업데이트"""
        self.progress_text.append(message)
    
    def display_results(self, articles):
        """크롤링 결과 표시"""
        self.articles = articles
        
        self.result_table.setRowCount(len(articles))
        
        for idx, article in enumerate(articles):
            # 번호
            item_num = QTableWidgetItem(str(idx + 1))
            item_num.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
            self.result_table.setItem(idx, 0, item_num)
            
            # 제목
            item_title = QTableWidgetItem(article['제목'])
            item_title.setToolTip(article['제목'])  # 마우스 오버시 전체 텍스트 표시
            self.result_table.setItem(idx, 1, item_title)
            
            # URL
            item_url = QTableWidgetItem(article['URL'])
            item_url.setToolTip(article['URL'])
            self.result_table.setItem(idx, 2, item_url)
            
            # 언론사
            item_press = QTableWidgetItem(article['언론사'])
            item_press.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
            self.result_table.setItem(idx, 3, item_press)
            
            # 작성일
            item_date = QTableWidgetItem(article['작성일'])
            item_date.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
            self.result_table.setItem(idx, 4, item_date)
    
    def crawling_finished(self):
        """크롤링 완료"""
        self.crawl_button.setEnabled(True)
        if self.articles:
            self.save_button.setEnabled(True)
            self.progress_text.append(f"\n✓ 크롤링 완료! 총 {len(self.articles)}개의 기사를 수집했습니다.")
        self.progress_bar.setValue(100)
    
    def show_error(self, error_message):
        """오류 표시"""
        self.crawl_button.setEnabled(True)
        QMessageBox.critical(self, '오류', error_message)
        self.progress_text.append(f"\n✗ {error_message}")
    
    def save_to_excel(self):
        """Excel 파일로 저장"""
        if not self.articles:
            QMessageBox.warning(self, '저장 오류', '저장할 데이터가 없습니다.')
            return
        
        # 파일 저장 대화상자
        file_path, _ = QFileDialog.getSaveFileName(
            self,
            '파일 저장',
            'naverResult.xlsx',
            'Excel 파일 (*.xlsx)'
        )
        
        if not file_path:
            return
        
        try:
            # Workbook 생성
            wb = Workbook()
            ws = wb.active
            ws.title = '뉴스'
            
            # 헤더 설정
            headers = ['번호', '제목', 'URL', '언론사', '작성일']
            ws.append(headers)
            
            # 헤더 스타일
            for cell in ws[1]:
                cell.font = Font(bold=True)
                cell.alignment = Alignment(horizontal='center', vertical='center')
            
            # 데이터 입력
            for idx, article in enumerate(self.articles, 1):
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
            wb.save(file_path)
            
            QMessageBox.information(
                self,
                '저장 완료',
                f'✓ {len(self.articles)}개의 기사가 저장되었습니다.\n파일: {file_path}'
            )
            
        except Exception as e:
            QMessageBox.critical(self, '저장 오류', f'파일 저장 중 오류가 발생했습니다.\n{str(e)}')


def main():
    app = QApplication(sys.argv)
    window = NaverNewsCrawlerGUI()
    window.show()
    sys.exit(app.exec())


if __name__ == '__main__':
    main()
