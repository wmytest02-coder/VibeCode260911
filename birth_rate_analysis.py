import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
from pathlib import Path

# 한글 폰트 설정 (Windows)
plt.rcParams['font.family'] = 'Malgun Gothic'
plt.rcParams['axes.unicode_minus'] = False

# 1. 엑셀 파일 로드
file_path = Path('c:/work/출생아수_data.xlsx')

print("=" * 80)
print("🔍 엑셀 파일 로드 및 데이터 구조 확인")
print("=" * 80)

# 엑셀 파일의 시트 확인
excel_file = pd.ExcelFile(file_path)
print(f"\n📄 시트 목록: {excel_file.sheet_names}")

# 첫 번째 시트 로드
df_raw = pd.read_excel(file_path, sheet_name=0)

print(f"\n📊 원본 데이터 크기: {df_raw.shape}")
print(f"\n첫 5행:\n{df_raw.head()}")
print(f"\n원본 구조 (행: 지표, 열: 연도):\n{df_raw}")

# 2. 데이터 변환 및 클랜징
print("\n" + "=" * 80)
print("🧹 데이터 변환 및 클랜징")
print("=" * 80)

# Wide format을 Long format으로 변환
df_long = pd.melt(df_raw, id_vars=['기본항목별'], 
                  var_name='연도', value_name='값')

# 연도 컬럼 정리 (예: '2025 p)' -> 2025)
df_long['연도'] = df_long['연도'].str.replace(' p)', '', regex=False)
df_long['연도'] = pd.to_numeric(df_long['연도'], errors='coerce')

print(f"\n변환된 데이터 크기: {df_long.shape}")
print(f"변환된 데이터:\n{df_long.head(10)}")

# 출생아수(명) 데이터만 선택
df_birth = df_long[df_long['기본항목별'] == '출생아수(명)'].copy()
df_birth = df_birth.dropna()

print(f"\n📊 출생아수 데이터 크기: {df_birth.shape}")
print(f"첫 5행:\n{df_birth.head()}")

# 3. 1970-2025년 데이터 필터링
print("\n" + "=" * 80)
print("📅 1970-2025년 데이터 필터링")
print("=" * 80)

df_filtered = df_birth[(df_birth['연도'] >= 1970) & (df_birth['연도'] <= 2025)].copy()
df_filtered = df_filtered.sort_values('연도').reset_index(drop=True)

print(f"\n✅ 필터링된 데이터 크기: {df_filtered.shape}")
print(f"연도 범위: {df_filtered['연도'].min():.0f} ~ {df_filtered['연도'].max():.0f}")
print(f"\n필터링된 데이터:\n{df_filtered}")

# 4. 다각도 분석
print("\n" + "=" * 80)
print("📈 다각도 분석: 출생아수(명)")
print("=" * 80)

birth_values = df_filtered['값'].astype(float)

print(f"\n【기본 통계】")
print(f"  ✓ 최대값: {birth_values.max():,.0f}명 (연도: {df_filtered.loc[birth_values.idxmax(), '연도']:.0f}년)")
print(f"  ✓ 최소값: {birth_values.min():,.0f}명 (연도: {df_filtered.loc[birth_values.idxmin(), '연도']:.0f}년)")
print(f"  ✓ 평균: {birth_values.mean():,.0f}명")
print(f"  ✓ 중앙값: {birth_values.median():,.0f}명")
print(f"  ✓ 표준편차: {birth_values.std():,.0f}명")

# 시대별 분석
print(f"\n【시대별 분석】")
periods = {
    '1970~1979': (1970, 1979),
    '1980~1989': (1980, 1989),
    '1990~1999': (1990, 1999),
    '2000~2009': (2000, 2009),
    '2010~2019': (2010, 2019),
    '2020~2025': (2020, 2025)
}

for period_name, (start_year, end_year) in periods.items():
    period_data = df_filtered[(df_filtered['연도'] >= start_year) & 
                              (df_filtered['연도'] <= end_year)]['값'].astype(float)
    if len(period_data) > 0:
        print(f"\n  📍 {period_name}년대")
        print(f"    - 평균 출생아수: {period_data.mean():,.0f}명")
        print(f"    - 최대/최소: {period_data.max():,.0f} / {period_data.min():,.0f}명")
        print(f"    - 증감: {((period_data.iloc[-1] - period_data.iloc[0]) / period_data.iloc[0] * 100):.2f}%")

# 변화율 분석
total_change = ((birth_values.iloc[-1] - birth_values.iloc[0]) / birth_values.iloc[0] * 100)
print(f"\n【전체 변화】")
print(f"  ✓ 1970년 ~ 2025년 변화율: {total_change:.2f}%")
print(f"  ✓ 절대 감소량: {(birth_values.iloc[-1] - birth_values.iloc[0]):,.0f}명")

# 5. 라인 그래프 생성
print("\n" + "=" * 80)
print("📊 라인 그래프 생성")
print("=" * 80)

fig, ax = plt.subplots(figsize=(15, 8))

# 주요 연도 강조
years = df_filtered['연도'].astype(int).values
values = df_filtered['값'].astype(float).values

ax.plot(years, values, marker='o', linewidth=2.5, markersize=6, 
        color='#FF6B6B', label='출생아수', zorder=2)

# 최대값과 최소값 표시
max_idx = values.argmax()
min_idx = values.argmin()

ax.scatter([years[max_idx]], [values[max_idx]], s=200, color='#FFD700', 
          edgecolors='red', linewidth=2, zorder=3, label=f'최대 ({years[max_idx]:.0f}년: {values[max_idx]:,.0f}명)')
ax.scatter([years[min_idx]], [values[min_idx]], s=200, color='#87CEEB', 
          edgecolors='blue', linewidth=2, zorder=3, label=f'최소 ({years[min_idx]:.0f}년: {values[min_idx]:,.0f}명)')

# 레이블 추가
ax.annotate(f'{values[max_idx]:,.0f}', xy=(years[max_idx], values[max_idx]), 
           xytext=(10, 10), textcoords='offset points', fontsize=10, fontweight='bold',
           bbox=dict(boxstyle='round,pad=0.5', facecolor='yellow', alpha=0.7))
ax.annotate(f'{values[min_idx]:,.0f}', xy=(years[min_idx], values[min_idx]), 
           xytext=(10, -20), textcoords='offset points', fontsize=10, fontweight='bold',
           bbox=dict(boxstyle='round,pad=0.5', facecolor='lightblue', alpha=0.7))

ax.set_xlabel('연도', fontsize=13, fontweight='bold')
ax.set_ylabel('출생아수 (명)', fontsize=13, fontweight='bold')
ax.set_title('한국 출생아수 추이 (1970년 ~ 2025년)', 
            fontsize=15, fontweight='bold', pad=20)

ax.grid(True, alpha=0.3, linestyle='--', linewidth=0.8)
ax.legend(fontsize=11, loc='upper right', framealpha=0.95)

# x축 연도 간격 조정
year_ticks = range(1970, 2030, 5)
ax.set_xticks(year_ticks)
ax.tick_params(axis='x', rotation=45, labelsize=10)
ax.tick_params(axis='y', labelsize=10)

# y축 포맷 설정 (천 단위 쉼표)
ax.yaxis.set_major_formatter(plt.FuncFormatter(lambda x, p: f'{int(x):,}'))

# 배경 설정
ax.set_facecolor('#f8f9fa')
fig.patch.set_facecolor('white')

plt.tight_layout()
plt.savefig('c:/work/birth_rate_line_graph.png', dpi=300, bbox_inches='tight')
print(f"\n✅ 그래프 저장: c:/work/birth_rate_line_graph.png")

plt.show()

# 6. 추가 분석 - 연도별 증감률
print("\n" + "=" * 80)
print("📊 추가 분석: 연도별 증감률")
print("=" * 80)

df_filtered_sorted = df_filtered.sort_values('연도').reset_index(drop=True)
df_filtered_sorted['증감률(%)'] = df_filtered_sorted['값'].pct_change() * 100

print(f"\n【출생아수 가장 많이 증가한 연도 Top 5】")
top_increase = df_filtered_sorted.nlargest(5, '증감률(%)')[['연도', '값', '증감률(%)']]
for idx, row in top_increase.iterrows():
    print(f"  {int(row['연도']):.0f}년: {row['값']:>10,.0f}명 (전년대비 +{row['증감률(%)']:>6.2f}%)")

print(f"\n【출생아수 가장 많이 감소한 연도 Top 5】")
top_decrease = df_filtered_sorted.nsmallest(5, '증감률(%)')[['연도', '값', '증감률(%)']]
for idx, row in top_decrease.iterrows():
    print(f"  {int(row['연도']):.0f}년: {row['값']:>10,.0f}명 (전년대비 {row['증감률(%)']:>6.2f}%)")

print("\n" + "=" * 80)
print("✨ 분석 완료!")
print("=" * 80)
