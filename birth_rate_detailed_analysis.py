import pandas as pd
import matplotlib
matplotlib.use('Agg')  # 비대화형 백엔드 설정
import matplotlib.pyplot as plt
import numpy as np
from pathlib import Path
from matplotlib import rcParams

# 한글 폰트 설정
rcParams['font.family'] = 'Malgun Gothic'
rcParams['axes.unicode_minus'] = False

# 데이터 로드 및 전처리
file_path = Path('c:/work/출생아수_data.xlsx')
df_raw = pd.read_excel(file_path, sheet_name=0)

# Wide format을 Long format으로 변환
df_long = pd.melt(df_raw, id_vars=['기본항목별'], var_name='연도', value_name='값')
df_long['연도'] = df_long['연도'].str.replace(' p)', '', regex=False)
df_long['연도'] = pd.to_numeric(df_long['연도'], errors='coerce')

# 출생아수 데이터 추출
df_birth = df_long[df_long['기본항목별'] == '출생아수(명)'].copy()
df_birth = df_birth[(df_birth['연도'] >= 1970) & (df_birth['연도'] <= 2025)].copy()
df_birth = df_birth.sort_values('연도').reset_index(drop=True)

years = df_birth['연도'].astype(int).values
values = df_birth['값'].astype(float).values

# 증감률 계산
df_birth['연년 증감률'] = df_birth['값'].pct_change() * 100

print("=" * 80)
print("📊 한국 출생아수 종합 분석 및 시각화")
print("=" * 80)

# 1. 다중 시각화 생성
fig = plt.figure(figsize=(18, 12))
gs = fig.add_gridspec(3, 2, hspace=0.3, wspace=0.3)

# [1] 메인 라인 그래프 - 전체 기간
ax1 = fig.add_subplot(gs[0, :])
ax1.plot(years, values, marker='o', linewidth=3, markersize=5, color='#FF6B6B', label='출생아수')
ax1.fill_between(years, values, alpha=0.2, color='#FF6B6B')
ax1.set_xlabel('연도', fontsize=12, fontweight='bold')
ax1.set_ylabel('출생아수 (명)', fontsize=12, fontweight='bold')
ax1.set_title('한국 출생아수 추이 (1970~2025년)', fontsize=14, fontweight='bold')
ax1.grid(True, alpha=0.3, linestyle='--')
ax1.yaxis.set_major_formatter(plt.FuncFormatter(lambda x, p: f'{int(x/1000)}만'))
ax1.legend(fontsize=11, loc='upper right')

# [2] 10년 단위 변화율
ax2 = fig.add_subplot(gs[1, 0])
decades = ['1970s', '1980s', '1990s', '2000s', '2010s', '2020s']
decade_changes = [-14.30, -25.89, -4.47, -30.50, -35.62, -6.61]
colors = ['red' if x < -20 else 'orange' if x < -10 else 'yellow' for x in decade_changes]

bars = ax2.bar(decades, decade_changes, color=colors, edgecolor='black', linewidth=1.5)
ax2.axhline(y=0, color='black', linestyle='-', linewidth=0.8)
ax2.set_ylabel('변화율 (%)', fontsize=11, fontweight='bold')
ax2.set_title('10년 단위 출생아수 변화율', fontsize=12, fontweight='bold')
ax2.grid(True, alpha=0.3, axis='y')

# 값 표시
for bar, val in zip(bars, decade_changes):
    height = bar.get_height()
    ax2.text(bar.get_x() + bar.get_width()/2., height,
            f'{val:.1f}%', ha='center', va='bottom' if height < 0 else 'top', fontweight='bold')

# [3] 시대별 평균 비교
ax3 = fig.add_subplot(gs[1, 1])
periods = ['1970~79', '1980~89', '1990~99', '2000~09', '2010~19', '2020~25']
period_avgs = [898164, 721037, 687060, 496696, 412981, 250795]

bars3 = ax3.barh(periods, period_avgs, color='#4ECDC4', edgecolor='black', linewidth=1.5)
ax3.set_xlabel('평균 출생아수 (명)', fontsize=11, fontweight='bold')
ax3.set_title('시대별 평균 출생아수', fontsize=12, fontweight='bold')
ax3.xaxis.set_major_formatter(plt.FuncFormatter(lambda x, p: f'{int(x/1000)}만'))
ax3.grid(True, alpha=0.3, axis='x')

# 값 표시
for bar, val in zip(bars3, period_avgs):
    width = bar.get_width()
    ax3.text(width, bar.get_y() + bar.get_height()/2.,
            f'{int(val):,}', ha='left', va='center', fontweight='bold', fontsize=9)

# [4] 연년 증감률
ax4 = fig.add_subplot(gs[2, 0])
valid_rates = df_birth['연년 증감률'].dropna().values
valid_years = years[1:]

colors_rate = ['red' if x < 0 else 'green' for x in valid_rates]
ax4.bar(valid_years, valid_rates, color=colors_rate, alpha=0.7, width=0.6, edgecolor='black', linewidth=0.5)
ax4.axhline(y=0, color='black', linestyle='-', linewidth=1)
ax4.set_xlabel('연도', fontsize=11, fontweight='bold')
ax4.set_ylabel('증감률 (%)', fontsize=11, fontweight='bold')
ax4.set_title('연년 증감률 변화', fontsize=12, fontweight='bold')
ax4.grid(True, alpha=0.3, axis='y')
ax4.set_xticks(range(1970, 2030, 5))
ax4.tick_params(axis='x', rotation=45)

# [5] 주요 기간 비교 박스 플롯
ax5 = fig.add_subplot(gs[2, 1])

period_data = {
    '1970s': values[0:10],
    '1980s': values[10:20],
    '1990s': values[20:30],
    '2000s': values[30:40],
    '2010s': values[40:50],
    '2020s': values[50:56]
}

bp = ax5.boxplot(period_data.values(), labels=period_data.keys(), patch_artist=True)
for patch, color in zip(bp['boxes'], ['#FFB6B9', '#FEC8D8', '#FFDFD3', '#E1F4D8', '#D4F1E4', '#B5EAD7']):
    patch.set_facecolor(color)
    patch.set_edgecolor('black')
    patch.set_linewidth(1.5)

ax5.set_ylabel('출생아수 (명)', fontsize=11, fontweight='bold')
ax5.set_title('시대별 출생아수 분포', fontsize=12, fontweight='bold')
ax5.yaxis.set_major_formatter(plt.FuncFormatter(lambda x, p: f'{int(x/1000)}만'))
ax5.grid(True, alpha=0.3, axis='y')

plt.suptitle('한국 출생아수 다각도 분석 대시보드 (1970~2025)', 
             fontsize=16, fontweight='bold', y=0.995)

plt.savefig('c:/work/birth_rate_comprehensive_analysis.png', dpi=300, bbox_inches='tight')
print("\n✅ 종합 분석 그래프 저장: c:/work/birth_rate_comprehensive_analysis.png")

# plt.show() 제거 - 비대화형 모드

# 2. 추가 상세 분석
print("\n" + "=" * 80)
print("📋 상세 분석 결과")
print("=" * 80)

print(f"\n【주요 통계】")
print(f"  ▪ 최고점: {values.max():,.0f}명 ({years[values.argmax()]:.0f}년)")
print(f"  ▪ 최저점: {values.min():,.0f}명 ({years[values.argmin()]:.0f}년)")
print(f"  ▪ 평균값: {values.mean():,.0f}명")
print(f"  ▪ 중앙값: {np.median(values):,.0f}명")
print(f"  ▪ 표준편차: {values.std():,.0f}명")

print(f"\n【시대별 순위 (평균 출생아수)】")
periods_info = [
    ('1970~79년대', 898164),
    ('1980~89년대', 721037),
    ('1990~99년대', 687060),
    ('2000~09년대', 496696),
    ('2010~19년대', 412981),
    ('2020~25년대', 250795)
]
for i, (period, avg) in enumerate(sorted(periods_info, key=lambda x: x[1], reverse=True), 1):
    print(f"  {i}위. {period}: {avg:,}명")

print(f"\n【급격한 변화 시기】")
# 가장 큰 감소와 증가
max_decrease_idx = df_birth['연년 증감률'].idxmin()
max_increase_idx = df_birth['연년 증감률'].idxmax()

print(f"  ▪ 최대 감소: {years[max_decrease_idx+1]:.0f}년 ({df_birth.loc[max_decrease_idx, '연년 증감률']:.2f}%)")
print(f"  ▪ 최대 증가: {years[max_increase_idx+1]:.0f}년 ({df_birth.loc[max_increase_idx, '연년 증감률']:.2f}%)")

print(f"\n【연도별 기록】")
# 100만 돌파
million_idx = np.where(values >= 1000000)[0]
if len(million_idx) > 0:
    print(f"  ▪ 100만 명 이상: {years[million_idx].min():.0f}~{years[million_idx].max():.0f}년")

# 50만 이하 진입
under_500k_idx = np.where(values < 500000)[0]
if len(under_500k_idx) > 0:
    print(f"  ▪ 50만 명 미만 진입: {years[under_500k_idx].min():.0f}년")

# 30만 이하 진입
under_300k_idx = np.where(values < 300000)[0]
if len(under_300k_idx) > 0:
    print(f"  ▪ 30만 명 미만 진입: {years[under_300k_idx].min():.0f}년")

print(f"\n【전망】")
print(f"  ▪ 1970년 대비 2025년: {((values[-1] - values[0]) / values[0] * 100):.2f}% 변화")
print(f"  ▪ 절대 감소량: {(values[0] - values[-1]):,.0f}명")
print(f"  ▪ 연평균 감소율: {((((values[-1] / values[0]) ** (1/(len(years)-1)) - 1) * 100)):.3f}%")

print("\n" + "=" * 80)
print("✨ 분석 완료!")
print("=" * 80)
