"""
YouTube Channel Analysis & Visualization System
- 채널 전수조사 및 히트/저조 영상 분류
- 경쟁사 비교 분석
- 블로그 글 자동 생성
"""

import json
import random
from datetime import datetime, timedelta
from collections import Counter
import math

# ═══════════════════════════════════════════════════════════════════════════
# 1. 데모 데이터 생성 (실제로는 YouTube API에서 가져옴)
# ═══════════════════════════════════════════════════════════════════════════

def generate_channel_data(channel_name, subscriber_base=100000, video_count=100):
    """채널 데이터 생성"""
    now = datetime.now()
    videos = []

    # 콘텐츠 키워드 풀
    keywords_pool = {
        '테크 리뷰 채널': ['리뷰', '언박싱', '비교', '추천', '꿀팁', '성능', '테스트', '가성비'],
        '브이로그 채널': ['일상', '브이로그', '하루', '여행', '맛집', '카페', 'VLOG', '데이트'],
        '요리 채널': ['레시피', '요리', '간단', '초간단', '집밥', '자취', '야식', '먹방'],
    }

    # 채널 타입 결정
    channel_type = random.choice(list(keywords_pool.keys()))
    keywords = keywords_pool[channel_type]

    for i in range(video_count):
        days_ago = random.randint(1, 365)
        publish_date = now - timedelta(days=days_ago)

        # 조회수 분포 (롱테일)
        base_views = random.lognormvariate(10, 1.5)
        views = int(min(base_views, 2000000))

        # 좋아요/댓글은 조회수에 비례
        engagement_rate = random.uniform(0.01, 0.08)
        likes = int(views * engagement_rate * random.uniform(0.6, 1.0))
        comments = int(likes * random.uniform(0.05, 0.2))

        # 제목 생성
        keyword = random.choice(keywords)
        title_templates = [
            f"[{keyword}] 이거 진짜 대박입니다",
            f"{keyword} 완벽 정리 | 꼭 봐야하는 영상",
            f"드디어 공개! {keyword} 끝판왕",
            f"{keyword} 리얼 후기 (솔직하게)",
            f"요즘 핫한 {keyword} 다 써봤습니다",
        ]

        videos.append({
            'id': f'video_{i}',
            'title': random.choice(title_templates),
            'published_at': publish_date.isoformat(),
            'views': views,
            'likes': likes,
            'comments': comments,
            'duration_minutes': random.randint(3, 45),
            'keyword': keyword,
            'hour': publish_date.hour,
            'day_of_week': publish_date.strftime('%A')
        })

    return {
        'name': channel_name,
        'type': channel_type,
        'subscribers': subscriber_base + random.randint(-30000, 50000),
        'total_videos': video_count,
        'videos': videos,
        'created_at': (now - timedelta(days=random.randint(365, 1500))).isoformat()
    }


# ═══════════════════════════════════════════════════════════════════════════
# 2. 분석 엔진 (히트/저조 영상 분류)
# ═══════════════════════════════════════════════════════════════════════════

def classify_videos(videos):
    """영상 성과 분류 (표준편차 기반)"""
    view_counts = [v['views'] for v in videos]
    avg = sum(view_counts) / len(view_counts)

    # 표준편차 계산
    variance = sum((v - avg) ** 2 for v in view_counts) / len(view_counts)
    std_dev = math.sqrt(variance)

    classified = []
    for video in videos:
        views = video['views']
        engagement_rate = ((video['likes'] + video['comments']) / views * 100) if views > 0 else 0

        # 등급 분류
        if views >= avg + std_dev * 1.5:
            tier = 'viral'
            tier_label = '🔥 바이럴'
            tier_color = '#EF4444'
        elif views >= avg + std_dev * 0.5:
            tier = 'hit'
            tier_label = '⭐ 히트'
            tier_color = '#F59E0B'
        elif views <= avg - std_dev:
            tier = 'underperform'
            tier_label = '📉 저조'
            tier_color = '#3B82F6'
        else:
            tier = 'average'
            tier_label = '평균'
            tier_color = '#6B7280'

        classified.append({
            **video,
            'engagement_rate': round(engagement_rate, 2),
            'tier': tier,
            'tier_label': tier_label,
            'tier_color': tier_color
        })

    return sorted(classified, key=lambda x: x['views'], reverse=True), {
        'avg_views': int(avg),
        'std_dev': int(std_dev),
        'viral_threshold': int(avg + std_dev * 1.5),
        'hit_threshold': int(avg + std_dev * 0.5)
    }


def analyze_upload_patterns(videos):
    """업로드 패턴 분석"""
    hour_counts = Counter(v['hour'] for v in videos)
    day_counts = Counter(v['day_of_week'] for v in videos)

    day_names_ko = {
        'Monday': '월', 'Tuesday': '화', 'Wednesday': '수',
        'Thursday': '목', 'Friday': '금', 'Saturday': '토', 'Sunday': '일'
    }

    hour_data = [{'hour': f'{h}시', 'count': hour_counts.get(h, 0)} for h in range(24)]
    day_data = [{'day': day_names_ko.get(d, d), 'count': day_counts.get(d, 0)}
                for d in ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']]

    # 최적 업로드 시간
    best_hour = max(hour_counts.keys(), key=lambda x: hour_counts[x]) if hour_counts else 18
    best_day = max(day_counts.keys(), key=lambda x: day_counts[x]) if day_counts else 'Wednesday'

    return {
        'hour_data': hour_data,
        'day_data': day_data,
        'best_hour': best_hour,
        'best_day': day_names_ko.get(best_day, best_day)
    }


def analyze_keywords(videos):
    """키워드 빈도 분석"""
    keywords = Counter(v['keyword'] for v in videos)
    return [{'word': word, 'count': count} for word, count in keywords.most_common(20)]


def calculate_monthly_trends(videos):
    """월별 트렌드 분석"""
    monthly = {}
    for v in videos:
        month_key = v['published_at'][:7]  # YYYY-MM
        if month_key not in monthly:
            monthly[month_key] = {
                'month': month_key,
                'total_views': 0,
                'total_likes': 0,
                'total_comments': 0,
                'video_count': 0,
                'hit_count': 0,
                'viral_count': 0
            }
        monthly[month_key]['total_views'] += v['views']
        monthly[month_key]['total_likes'] += v['likes']
        monthly[month_key]['total_comments'] += v['comments']
        monthly[month_key]['video_count'] += 1
        if v.get('tier') == 'hit':
            monthly[month_key]['hit_count'] += 1
        if v.get('tier') == 'viral':
            monthly[month_key]['viral_count'] += 1

    return sorted(monthly.values(), key=lambda x: x['month'])[-12:]


# ═══════════════════════════════════════════════════════════════════════════
# 3. 경쟁사 비교 분석
# ═══════════════════════════════════════════════════════════════════════════

def compare_channels(channels_data):
    """다중 채널 비교 분석"""
    comparison = []
    for ch in channels_data:
        classified, _ = classify_videos(ch['videos'])
        total_views = sum(v['views'] for v in ch['videos'])
        hit_videos = [v for v in classified if v['tier'] in ['hit', 'viral']]
        avg_engagement = sum(v['engagement_rate'] for v in classified) / len(classified) if classified else 0

        comparison.append({
            'name': ch['name'],
            'subscribers': ch['subscribers'],
            'total_views': total_views,
            'video_count': ch['total_videos'],
            'avg_views_per_video': int(total_views / ch['total_videos']),
            'hit_rate': round(len(hit_videos) / len(classified) * 100, 1) if classified else 0,
            'avg_engagement': round(avg_engagement, 2),
            'channel_type': ch['type']
        })

    return comparison


def generate_radar_data(comparison_data):
    """레이더 차트용 정규화 데이터"""
    if not comparison_data:
        return []

    metrics = ['subscribers', 'total_views', 'avg_views_per_video', 'hit_rate', 'avg_engagement']
    metric_labels = ['구독자', '총 조회수', '영상당 조회수', '히트율', '참여율']

    radar_data = []
    for i, metric in enumerate(metrics):
        max_val = max(ch[metric] for ch in comparison_data)
        entry = {'metric': metric_labels[i]}
        for ch in comparison_data:
            entry[ch['name']] = round(ch[metric] / max_val * 100, 1) if max_val > 0 else 0
        radar_data.append(entry)

    return radar_data


# ═══════════════════════════════════════════════════════════════════════════
# 4. 결과 리포트 생성
# ═══════════════════════════════════════════════════════════════════════════

def format_number(num):
    """숫자 포맷팅"""
    if num >= 1000000:
        return f'{num/1000000:.1f}M'
    elif num >= 1000:
        return f'{num/1000:.1f}K'
    return str(num)


def generate_analysis_report(channel_data, classified_videos, stats, upload_patterns, monthly_trends):
    """분석 리포트 생성"""
    tier_distribution = Counter(v['tier'] for v in classified_videos)
    total_views = sum(v['views'] for v in classified_videos)

    report = f"""
╔══════════════════════════════════════════════════════════════════════════════╗
║                        📊 YouTube 채널 분석 리포트                              ║
╠══════════════════════════════════════════════════════════════════════════════╣
║  채널명: {channel_data['name']:<50}                     ║
║  채널 유형: {channel_data['type']:<48}                  ║
║  분석 일시: {datetime.now().strftime('%Y-%m-%d %H:%M'):<47}                   ║
╚══════════════════════════════════════════════════════════════════════════════╝

┌──────────────────────────────────────────────────────────────────────────────┐
│                              📈 핵심 지표 (KPI)                               │
├──────────────────────────────────────────────────────────────────────────────┤
│                                                                              │
│   👥 구독자          👁️ 총 조회수         🎬 영상 수          ⚡ 히트율         │
│   {format_number(channel_data['subscribers']):>10}         {format_number(total_views):>12}          {channel_data['total_videos']:>8}개         {(tier_distribution.get('hit', 0) + tier_distribution.get('viral', 0)) / len(classified_videos) * 100:>6.1f}%        │
│                                                                              │
└──────────────────────────────────────────────────────────────────────────────┘

┌──────────────────────────────────────────────────────────────────────────────┐
│                           🏆 영상 성과 분포                                    │
├──────────────────────────────────────────────────────────────────────────────┤
│                                                                              │
│   🔥 바이럴 (상위 7%)    : {tier_distribution.get('viral', 0):>4}개  ({tier_distribution.get('viral', 0)/len(classified_videos)*100:>5.1f}%)                          │
│   ⭐ 히트 (상위 30%)     : {tier_distribution.get('hit', 0):>4}개  ({tier_distribution.get('hit', 0)/len(classified_videos)*100:>5.1f}%)                          │
│   📊 평균               : {tier_distribution.get('average', 0):>4}개  ({tier_distribution.get('average', 0)/len(classified_videos)*100:>5.1f}%)                          │
│   📉 저조 (하위 16%)    : {tier_distribution.get('underperform', 0):>4}개  ({tier_distribution.get('underperform', 0)/len(classified_videos)*100:>5.1f}%)                          │
│                                                                              │
│   ─────────────────────────────────────────────────────────                  │
│   분류 기준: 평균 조회수 {format_number(stats['avg_views'])} / 표준편차 {format_number(stats['std_dev'])}                         │
│   바이럴 기준: {format_number(stats['viral_threshold'])}+ / 히트 기준: {format_number(stats['hit_threshold'])}+                      │
│                                                                              │
└──────────────────────────────────────────────────────────────────────────────┘

┌──────────────────────────────────────────────────────────────────────────────┐
│                          ⏰ 업로드 패턴 분석                                   │
├──────────────────────────────────────────────────────────────────────────────┤
│                                                                              │
│   📅 최적 업로드 요일: {upload_patterns['best_day']}요일                                          │
│   🕐 최적 업로드 시간: {upload_patterns['best_hour']}시                                           │
│                                                                              │
│   시간대별 분포:                                                              │
│   """

    # 시간대 막대 그래프
    max_hour_count = max(h['count'] for h in upload_patterns['hour_data']) or 1
    for i in range(0, 24, 4):
        counts = [upload_patterns['hour_data'][j]['count'] for j in range(i, min(i+4, 24))]
        bars = ['█' * int(c / max_hour_count * 10) for c in counts]
        report += f"\n│   {i:02d}시-{i+3:02d}시: " + " | ".join(f"{bars[j]:10}" for j in range(len(bars))) + "│"

    report += f"""
│                                                                              │
└──────────────────────────────────────────────────────────────────────────────┘

┌──────────────────────────────────────────────────────────────────────────────┐
│                          🏅 TOP 10 히트 영상                                  │
├──────────────────────────────────────────────────────────────────────────────┤
"""

    for i, video in enumerate(classified_videos[:10], 1):
        title = video['title'][:30] + '...' if len(video['title']) > 30 else video['title']
        report += f"│ {i:2}. {video['tier_label']:8} │ {title:<35} │ {format_number(video['views']):>8} views │\n"

    report += """└──────────────────────────────────────────────────────────────────────────────┘
"""

    return report


def generate_comparison_report(comparison_data, radar_data):
    """경쟁사 비교 리포트"""
    report = f"""
╔══════════════════════════════════════════════════════════════════════════════╗
║                        🎯 경쟁사 비교 분석 리포트                              ║
╠══════════════════════════════════════════════════════════════════════════════╣
║  비교 채널 수: {len(comparison_data)}개                                                         ║
║  분석 일시: {datetime.now().strftime('%Y-%m-%d %H:%M')}                                           ║
╚══════════════════════════════════════════════════════════════════════════════╝

┌──────────────────────────────────────────────────────────────────────────────┐
│                          📊 채널별 핵심 지표 비교                              │
├──────────────────────────────────────────────────────────────────────────────┤
│ 채널명          │ 구독자    │ 총 조회수  │ 영상당조회 │ 히트율  │ 참여율   │
├──────────────────────────────────────────────────────────────────────────────┤
"""

    for ch in comparison_data:
        name = ch['name'][:12] + '..' if len(ch['name']) > 14 else ch['name']
        report += f"│ {name:<14} │ {format_number(ch['subscribers']):>9} │ {format_number(ch['total_views']):>10} │ {format_number(ch['avg_views_per_video']):>10} │ {ch['hit_rate']:>6.1f}% │ {ch['avg_engagement']:>6.2f}% │\n"

    report += """└──────────────────────────────────────────────────────────────────────────────┘

┌──────────────────────────────────────────────────────────────────────────────┐
│                         🎯 레이더 차트 데이터 (정규화 %)                        │
├──────────────────────────────────────────────────────────────────────────────┤
"""

    for metric in radar_data:
        values = " │ ".join(f"{metric.get(ch['name'], 0):>6.1f}%" for ch in comparison_data)
        report += f"│ {metric['metric']:<12} │ {values} │\n"

    report += """└──────────────────────────────────────────────────────────────────────────────┘

┌──────────────────────────────────────────────────────────────────────────────┐
│                            💡 인사이트 요약                                   │
├──────────────────────────────────────────────────────────────────────────────┤
"""

    # 각 지표별 1위 찾기
    best_subs = max(comparison_data, key=lambda x: x['subscribers'])
    best_views = max(comparison_data, key=lambda x: x['total_views'])
    best_hit = max(comparison_data, key=lambda x: x['hit_rate'])
    best_engagement = max(comparison_data, key=lambda x: x['avg_engagement'])

    report += f"""│ 📈 구독자 1위: {best_subs['name']} ({format_number(best_subs['subscribers'])})                                │
│ 👁️ 조회수 1위: {best_views['name']} ({format_number(best_views['total_views'])})                               │
│ 🔥 히트율 1위: {best_hit['name']} ({best_hit['hit_rate']:.1f}%)                                          │
│ 💬 참여율 1위: {best_engagement['name']} ({best_engagement['avg_engagement']:.2f}%)                                       │
└──────────────────────────────────────────────────────────────────────────────┘
"""

    return report


# ═══════════════════════════════════════════════════════════════════════════
# 5. 블로그 글 생성
# ═══════════════════════════════════════════════════════════════════════════

def generate_blog_post(channel_data, classified_videos, stats, comparison_data=None):
    """분석 결과 기반 블로그 글 생성"""

    tier_distribution = Counter(v['tier'] for v in classified_videos)
    top_videos = classified_videos[:5]
    total_views = sum(v['views'] for v in classified_videos)
    hit_rate = (tier_distribution.get('hit', 0) + tier_distribution.get('viral', 0)) / len(classified_videos) * 100

    # 인기 키워드 추출
    keywords = analyze_keywords(classified_videos)
    top_keywords = [k['word'] for k in keywords[:5]]

    blog_post = f"""# {channel_data['name']} 채널 완벽 분석: 히트 영상의 비밀을 파헤치다

> **요약**: {channel_data['name']} 채널의 전체 {len(classified_videos)}개 영상을 분석한 결과,
> 히트율 {hit_rate:.1f}%로 업계 평균을 상회하는 성과를 보이고 있습니다.

---

## 📊 채널 핵심 지표

| 지표 | 수치 | 평가 |
|------|------|------|
| 구독자 수 | {format_number(channel_data['subscribers'])} | {'🔥 대형 채널' if channel_data['subscribers'] > 100000 else '📈 성장 중'} |
| 총 조회수 | {format_number(total_views)} | {'💎 높은 도달률' if total_views > 10000000 else '✅ 안정적'} |
| 영상 수 | {channel_data['total_videos']}개 | {'📚 풍부한 콘텐츠' if channel_data['total_videos'] > 50 else '🎯 선택과 집중'} |
| 히트율 | {hit_rate:.1f}% | {'🏆 최상위' if hit_rate > 30 else '👍 양호' if hit_rate > 15 else '📊 개선 필요'} |

---

## 🔥 히트 영상 패턴 분석

### 조회수 분포 현황

{channel_data['name']} 채널의 영상 성과를 표준편차 기반으로 분류한 결과:

- **🔥 바이럴 영상** ({tier_distribution.get('viral', 0)}개, {tier_distribution.get('viral', 0)/len(classified_videos)*100:.1f}%): 조회수 {format_number(stats['viral_threshold'])} 이상
- **⭐ 히트 영상** ({tier_distribution.get('hit', 0)}개, {tier_distribution.get('hit', 0)/len(classified_videos)*100:.1f}%): 조회수 {format_number(stats['hit_threshold'])} 이상
- **📊 평균 영상** ({tier_distribution.get('average', 0)}개, {tier_distribution.get('average', 0)/len(classified_videos)*100:.1f}%): 평균 수준 성과
- **📉 저조 영상** ({tier_distribution.get('underperform', 0)}개, {tier_distribution.get('underperform', 0)/len(classified_videos)*100:.1f}%): 기대 이하 성과

### TOP 5 히트 영상

"""

    for i, video in enumerate(top_videos, 1):
        blog_post += f"""#### {i}. {video['title']}
- **조회수**: {format_number(video['views'])}
- **좋아요**: {format_number(video['likes'])} / **댓글**: {format_number(video['comments'])}
- **참여율**: {video['engagement_rate']}%
- **성과 등급**: {video['tier_label']}

"""

    blog_post += f"""---

## 💡 성공 요인 분석

### 1. 콘텐츠 키워드 전략

{channel_data['name']} 채널에서 가장 자주 사용되는 키워드:

"""

    for i, kw in enumerate(keywords[:10], 1):
        blog_post += f"{i}. **{kw['word']}** ({kw['count']}회)\n"

    blog_post += f"""
### 2. 히트 영상의 공통점

분석 결과, 히트 영상들은 다음과 같은 공통점을 가지고 있습니다:

1. **제목 구조**: 호기심을 자극하는 키워드 ({', '.join(top_keywords[:3])}) 활용
2. **참여율**: 평균 {sum(v['engagement_rate'] for v in top_videos)/len(top_videos):.2f}%로 높은 시청자 반응
3. **콘텐츠 유형**: {channel_data['type']} 기반의 트렌드 반영

---

## 📈 콘텐츠 전략 제안

### 추천 전략

1. **키워드 최적화**: '{top_keywords[0]}', '{top_keywords[1] if len(top_keywords) > 1 else ""}' 키워드 적극 활용
2. **업로드 타이밍**: 분석된 최적 시간대에 맞춘 콘텐츠 발행
3. **참여 유도**: 댓글/좋아요 유도 CTA 강화로 알고리즘 최적화
4. **썸네일 전략**: 히트 영상의 썸네일 패턴 분석 및 적용

### 벤치마킹 포인트

- 바이럴 영상의 **제목 패턴** 학습
- 높은 참여율을 이끌어낸 **콘텐츠 구성** 분석
- 시청 지속 시간을 높이는 **편집 스타일** 연구

---

## 🎯 결론

{channel_data['name']} 채널은 **{hit_rate:.1f}%의 히트율**로 안정적인 성과를 보이고 있습니다.
특히 '{top_keywords[0]}' 관련 콘텐츠에서 강세를 보이며,
{tier_distribution.get('viral', 0)}개의 바이럴 영상이 전체 조회수의 상당 부분을 견인하고 있습니다.

향후 히트율을 더욱 높이기 위해서는:
- 검증된 키워드 전략의 지속적 활용
- 트렌드에 민감한 콘텐츠 기획
- 시청자 참여를 유도하는 커뮤니티 전략

이 세 가지에 집중할 것을 권장합니다.

---

*본 분석은 {datetime.now().strftime('%Y년 %m월 %d일')} 기준 데이터입니다.*
"""

    if comparison_data and len(comparison_data) > 1:
        blog_post += f"""
---

## 🏆 경쟁사 비교 분석

### 경쟁 채널 현황

| 채널명 | 구독자 | 총 조회수 | 히트율 | 참여율 |
|--------|--------|----------|--------|--------|
"""
        for ch in comparison_data:
            blog_post += f"| {ch['name']} | {format_number(ch['subscribers'])} | {format_number(ch['total_views'])} | {ch['hit_rate']:.1f}% | {ch['avg_engagement']:.2f}% |\n"

        best_hit = max(comparison_data, key=lambda x: x['hit_rate'])
        blog_post += f"""
### 경쟁 분석 인사이트

- **히트율 1위**: {best_hit['name']} ({best_hit['hit_rate']:.1f}%)
- **핵심 경쟁력**: 각 채널별 콘텐츠 차별화 전략 필요
- **기회 영역**: 경쟁사 대비 참여율 개선 여지 존재
"""

    return blog_post


# ═══════════════════════════════════════════════════════════════════════════
# 6. 메인 실행
# ═══════════════════════════════════════════════════════════════════════════

def main():
    print("=" * 80)
    print("🎬 YouTube 채널 분석 시스템 시작")
    print("=" * 80)

    # 1. 데모 채널 데이터 생성
    print("\n📥 채널 데이터 생성 중...")

    channels = [
        generate_channel_data("테크리뷰어_김기술", 150000, 120),
        generate_channel_data("일상브이로그_이하루", 85000, 80),
        generate_channel_data("요리왕_박셰프", 220000, 150),
    ]

    print(f"   ✅ {len(channels)}개 채널 데이터 생성 완료")

    # 2. 각 채널 분석
    all_results = []
    for channel in channels:
        print(f"\n🔍 '{channel['name']}' 채널 분석 중...")

        # 영상 분류
        classified, stats = classify_videos(channel['videos'])

        # 업로드 패턴 분석
        upload_patterns = analyze_upload_patterns(channel['videos'])

        # 월별 트렌드
        monthly_trends = calculate_monthly_trends(classified)

        # 키워드 분석
        keywords = analyze_keywords(channel['videos'])

        all_results.append({
            'channel': channel,
            'classified': classified,
            'stats': stats,
            'upload_patterns': upload_patterns,
            'monthly_trends': monthly_trends,
            'keywords': keywords
        })

        # 개별 채널 리포트 출력
        report = generate_analysis_report(
            channel, classified, stats, upload_patterns, monthly_trends
        )
        print(report)

    # 3. 경쟁사 비교 분석
    print("\n" + "=" * 80)
    print("🎯 경쟁사 비교 분석")
    print("=" * 80)

    comparison_data = compare_channels(channels)
    radar_data = generate_radar_data(comparison_data)

    comparison_report = generate_comparison_report(comparison_data, radar_data)
    print(comparison_report)

    # 4. 블로그 글 생성
    print("\n" + "=" * 80)
    print("📝 블로그 글 생성")
    print("=" * 80)

    # 첫 번째 채널 기준으로 블로그 생성
    main_result = all_results[0]
    blog_post = generate_blog_post(
        main_result['channel'],
        main_result['classified'],
        main_result['stats'],
        comparison_data
    )

    # 블로그 글 파일로 저장
    with open('blog_post.md', 'w', encoding='utf-8') as f:
        f.write(blog_post)

    print("\n✅ 블로그 글이 'blog_post.md' 파일로 저장되었습니다.")
    print("\n" + "-" * 80)
    print("📄 블로그 미리보기 (처음 50줄)")
    print("-" * 80)
    print('\n'.join(blog_post.split('\n')[:50]))
    print("\n... (전체 내용은 blog_post.md 파일 참조)")

    # 5. JSON 데이터 저장 (시각화용)
    visualization_data = {
        'channels': [
            {
                'name': r['channel']['name'],
                'subscribers': r['channel']['subscribers'],
                'total_videos': r['channel']['total_videos'],
                'type': r['channel']['type'],
                'stats': r['stats'],
                'tier_distribution': dict(Counter(v['tier'] for v in r['classified'])),
                'upload_patterns': r['upload_patterns'],
                'monthly_trends': r['monthly_trends'],
                'keywords': r['keywords'][:10],
                'top_videos': [
                    {
                        'title': v['title'],
                        'views': v['views'],
                        'likes': v['likes'],
                        'comments': v['comments'],
                        'engagement_rate': v['engagement_rate'],
                        'tier': v['tier'],
                        'tier_label': v['tier_label']
                    }
                    for v in r['classified'][:10]
                ]
            }
            for r in all_results
        ],
        'comparison': comparison_data,
        'radar_data': radar_data
    }

    with open('analysis_data.json', 'w', encoding='utf-8') as f:
        json.dump(visualization_data, f, ensure_ascii=False, indent=2)

    print("\n✅ 시각화 데이터가 'analysis_data.json' 파일로 저장되었습니다.")

    return visualization_data, blog_post


if __name__ == '__main__':
    data, blog = main()
