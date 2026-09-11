import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from datetime import datetime
import warnings

warnings.filterwarnings('ignore')

# 한글 폰트 설정
plt.rcParams['font.family'] = 'DejaVu Sans'
plt.rcParams['axes.unicode_minus'] = False

# ============================================
# 1. 데이터 로드 및 클랜징
# ============================================
print("=" * 60)
print("S&P 500 데이터 분석 시작")
print("=" * 60)

# CSV 파일 로드
df = pd.read_csv('S&P 500 과거 데이터.csv')

print("\n[1] 원본 데이터 정보:")
print(f"- 총 행 수: {len(df)}")
print(f"- 컬럼: {df.columns.tolist()}")
print(f"- 데이터 타입:\n{df.dtypes}")

# 데이터 클랜징
# 1. 날짜 정규화 (공백 제거)
df['날짜'] = df['날짜'].str.replace(' ', '')

# 2. 숫자 컬럼에서 쉼표 제거 및 타입 변환
for col in ['종가', '시가', '고가', '저가']:
    df[col] = df[col].astype(str).str.replace(',', '').astype(float)

# 3. 변동 % 정규화 (% 기호 제거)
df['변동 %'] = df['변동 %'].astype(str).str.replace('%', '').astype(float)

# 4. 날짜를 datetime 형식으로 변환
df['날짜'] = pd.to_datetime(df['날짜'], format='%Y-%m-%d')

# 5. 거래량 처리 (빈 값이므로 삭제 또는 NaN으로 처리)
df['거래량'] = pd.to_numeric(df['거래량'], errors='coerce')

# 6. 날짜 기준으로 오름차순 정렬 (2000년부터 2019년까지)
df = df.sort_values('날짜').reset_index(drop=True)

print("\n[2] 클랜징된 데이터 정보:")
print(f"- 시작 날짜: {df['날짜'].min().strftime('%Y-%m-%d')}")
print(f"- 종료 날짜: {df['날짜'].max().strftime('%Y-%m-%d')}")
print(f"\n원본 데이터 샘플:")
print(df.head(10))

# ============================================
# 2. 데이터 필터링 (2000년 1월 초 ~ 2019년 연말)
# ============================================
start_date = pd.to_datetime('2000-01-01')
end_date = pd.to_datetime('2019-12-31')

df_filtered = df[(df['날짜'] >= start_date) & (df['날짜'] <= end_date)].copy()

print(f"\n[3] 필터링된 데이터 (2000-01-01 ~ 2019-12-31):")
print(f"- 행 수: {len(df_filtered)}")
print(f"- 시작 날짜: {df_filtered['날짜'].min().strftime('%Y-%m-%d')}")
print(f"- 종료 날짜: {df_filtered['날짜'].max().strftime('%Y-%m-%d')}")

# ============================================
# 3. 다각도 분석
# ============================================
print("\n" + "=" * 60)
print("S&P 500 데이터 분석")
print("=" * 60)

# 기본 통계
print("\n[4] 기본 통계:")
print(df_filtered[['종가', '시가', '고가', '저가', '변동 %']].describe().round(2))

# 연도별 분석
print("\n[5] 연도별 종가 분석:")
df_filtered['연도'] = df_filtered['날짜'].dt.year
yearly_stats = df_filtered.groupby('연도').agg({
    '종가': ['first', 'last', 'min', 'max', 'mean'],
    '변동 %': 'mean'
}).round(2)
print(yearly_stats)

# 월별 평균 변동률
print("\n[6] 월별 평균 변동률:")
df_filtered['월'] = df_filtered['날짜'].dt.month
monthly_change = df_filtered.groupby('월')['변동 %'].mean().round(2)
print(monthly_change)

# 종가 상승/하락 일수
price_changes = df_filtered['변동 %'] > 0
print(f"\n[7] 상승/하락 통계:")
print(f"- 상승일: {price_changes.sum()} 일 ({price_changes.sum()/len(df_filtered)*100:.1f}%)")
print(f"- 하락일: {(~price_changes).sum()} 일 ({(~price_changes).sum()/len(df_filtered)*100:.1f}%)")

# 최대 상승/하락일
print(f"\n[8] 극단적 변동:")
print(f"- 최대 상승: {df_filtered['변동 %'].max():.2f}% ({df_filtered.loc[df_filtered['변동 %'].idxmax(), '날짜'].strftime('%Y-%m-%d')})")
print(f"- 최대 하락: {df_filtered['변동 %'].min():.2f}% ({df_filtered.loc[df_filtered['변동 %'].idxmin(), '날짜'].strftime('%Y-%m-%d')})")

# 20년간 수익률
initial_price = df_filtered.iloc[0]['종가']
final_price = df_filtered.iloc[-1]['종가']
total_return = (final_price - initial_price) / initial_price * 100
print(f"\n[9] 20년 수익률:")
print(f"- 초기 종가 (2000-01-03): {initial_price:.2f}")
print(f"- 최종 종가 (2019-12-31): {final_price:.2f}")
print(f"- 총 수익률: {total_return:.2f}%")

# ============================================
# 4. 시각화: 2000년 1월 초 ~ 2019년 연말 종가 라인 그래프
# ============================================
print("\n[10] 라인 그래프 생성 중...")

plt.figure(figsize=(16, 8))
plt.plot(df_filtered['날짜'], df_filtered['종가'], linewidth=2, color='#1f77b4', label='S&P 500 Close Price')

# 연도 표시 (세로 선)
for year in range(2000, 2020):
    year_date = pd.to_datetime(f'{year}-01-01')
    if year_date >= df_filtered['날짜'].min() and year_date <= df_filtered['날짜'].max():
        plt.axvline(x=year_date, color='gray', linestyle='--', alpha=0.3, linewidth=0.5)

plt.xlabel('Year', fontsize=12, fontweight='bold')
plt.ylabel('Close Price (USD)', fontsize=12, fontweight='bold')
plt.title('S&P 500 Close Price (2000-01-03 ~ 2019-12-31)', fontsize=14, fontweight='bold')

# x축 포맷팅
ax = plt.gca()
ax.xaxis.set_major_locator(mdates.YearLocator(2))  # 2년 간격
ax.xaxis.set_major_formatter(mdates.DateFormatter('%Y'))
plt.xticks(rotation=45)

# 그리드 추가
plt.grid(True, alpha=0.3, linestyle='-', linewidth=0.5)
plt.legend(fontsize=11, loc='upper left')
plt.tight_layout()

# 그래프 저장
plt.savefig('sp500_close_price_2000_2019.png', dpi=300, bbox_inches='tight')
print("✓ 그래프 저장: sp500_close_price_2000_2019.png")

plt.show()

# ============================================
# 5. 추가 시각화: 연도별 분석
# ============================================
print("\n[11] 추가 시각화 생성 중...")

fig, axes = plt.subplots(2, 2, figsize=(16, 10))

# 1. 연도별 종가 분포
yearly_min = df_filtered.groupby('연도')['종가'].min()
yearly_max = df_filtered.groupby('연도')['종가'].max()
yearly_close = df_filtered.groupby('연도')['종가'].last()

ax1 = axes[0, 0]
ax1.bar(yearly_min.index, yearly_max.index - yearly_min.index, bottom=yearly_min.values, alpha=0.7, color='skyblue')
ax1.plot(yearly_close.index, yearly_close.values, 'ro-', linewidth=2, markersize=6, label='Year-end Close')
ax1.set_xlabel('Year', fontsize=11, fontweight='bold')
ax1.set_ylabel('Price (USD)', fontsize=11, fontweight='bold')
ax1.set_title('Yearly Price Range and Year-end Close', fontsize=12, fontweight='bold')
ax1.legend()
ax1.grid(True, alpha=0.3)

# 2. 월별 평균 변동률
ax2 = axes[0, 1]
colors = ['green' if x > 0 else 'red' for x in monthly_change.values]
ax2.bar(monthly_change.index, monthly_change.values, color=colors, alpha=0.7)
ax2.axhline(y=0, color='black', linestyle='-', linewidth=0.8)
ax2.set_xlabel('Month', fontsize=11, fontweight='bold')
ax2.set_ylabel('Average Change (%)', fontsize=11, fontweight='bold')
ax2.set_title('Average Monthly Change Rate', fontsize=12, fontweight='bold')
ax2.set_xticks(range(1, 13))
ax2.grid(True, alpha=0.3, axis='y')

# 3. 종가 히스토그램
ax3 = axes[1, 0]
ax3.hist(df_filtered['종가'], bins=50, color='steelblue', alpha=0.7, edgecolor='black')
ax3.axvline(df_filtered['종가'].mean(), color='red', linestyle='--', linewidth=2, label=f"Mean: {df_filtered['종가'].mean():.2f}")
ax3.axvline(df_filtered['종가'].median(), color='green', linestyle='--', linewidth=2, label=f"Median: {df_filtered['종가'].median():.2f}")
ax3.set_xlabel('Close Price (USD)', fontsize=11, fontweight='bold')
ax3.set_ylabel('Frequency', fontsize=11, fontweight='bold')
ax3.set_title('Distribution of Close Price', fontsize=12, fontweight='bold')
ax3.legend()
ax3.grid(True, alpha=0.3, axis='y')

# 4. 일일 변동률 시계열
ax4 = axes[1, 1]
colors = ['green' if x > 0 else 'red' for x in df_filtered['변동 %'].values]
ax4.scatter(df_filtered['날짜'], df_filtered['변동 %'], c=colors, alpha=0.5, s=1)
ax4.axhline(y=0, color='black', linestyle='-', linewidth=0.8)
ax4.set_xlabel('Year', fontsize=11, fontweight='bold')
ax4.set_ylabel('Daily Change (%)', fontsize=11, fontweight='bold')
ax4.set_title('Daily Change Rate Over Time', fontsize=12, fontweight='bold')
ax4.grid(True, alpha=0.3)

plt.tight_layout()
plt.savefig('sp500_detailed_analysis.png', dpi=300, bbox_inches='tight')
print("✓ 그래프 저장: sp500_detailed_analysis.png")

plt.show()

print("\n" + "=" * 60)
print("분석 완료!")
print("=" * 60)
