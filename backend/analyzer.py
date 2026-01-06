"""
YouTube Channel Analysis Engine v3.0
유튜브 알고리즘 기반 분석 엔진 (2025-2026 알고리즘 반영)

핵심 알고리즘 요소:
- View Velocity (조회 속도): 업로드 후 일평균 조회수
- CTR 지표: 제목/썸네일 최적화 점수
- Engagement Rate: (좋아요 + 댓글) / 조회수
- Like Ratio: 좋아요 / 조회수 (만족도 신호)
- Comment Rate: 댓글 / 조회수 (참여 신호)

참고 자료:
- https://blog.hootsuite.com/youtube-algorithm/
- https://vidiq.com/blog/post/understanding-youtube-algorithm/
- https://socialbee.com/blog/youtube-algorithm/
"""
import statistics
from datetime import datetime, timedelta
from collections import Counter, defaultdict
import re
import json
import math


class ChannelAnalyzer:
    """채널 심층 분석기 - YouTube 알고리즘 기반 v3.0"""

    # YouTube 알고리즘 기반 성과 점수 가중치
    SCORE_WEIGHTS = {
        'view_velocity': 0.25,      # 조회 속도 (핵심!) 25%
        'engagement_rate': 0.20,    # 참여율 20%
        'like_ratio': 0.15,         # 좋아요 비율 (만족도) 15%
        'comment_rate': 0.10,       # 댓글율 10%
        'title_ctr_score': 0.15,    # 제목 CTR 점수 15%
        'duration_efficiency': 0.15, # 길이 대비 효율 15%
    }

    # YouTube 알고리즘 벤치마크 (2025-2026 기준)
    YOUTUBE_BENCHMARKS = {
        'ctr': {'excellent': 7.0, 'good': 5.0, 'average': 4.0, 'poor': 2.0},
        'retention': {'excellent': 70, 'good': 50, 'average': 40, 'poor': 30},
        'like_ratio': {'excellent': 5.0, 'good': 3.0, 'average': 2.0, 'poor': 1.0},
        'engagement_rate': {'excellent': 8.0, 'good': 5.0, 'average': 3.0, 'poor': 1.5},
        'comment_rate': {'excellent': 0.5, 'good': 0.3, 'average': 0.1, 'poor': 0.05},
    }

    # 제목 CTR 최적화 키워드 (한국어)
    CTR_BOOST_KEYWORDS = {
        'curiosity': ['비밀', '충격', '진실', '알려드', '몰랐던', '실제로', '결국', '드디어'],
        'numbers': [r'\d+가지', r'\d+개', r'\d+%', r'\d+만', r'TOP\s*\d+', r'\d+위'],
        'urgency': ['지금', '바로', '즉시', '오늘', '당장', '필수'],
        'value': ['무료', '꿀팁', '핵심', '완벽', '최고', '추천', '방법', '비법'],
        'emotion': ['대박', '미쳤', '놀라운', '충격', '감동', '웃긴', '레전드'],
        'question': [r'\?$', '왜', '어떻게', '무엇', '언제', '어디서'],
    }

    def __init__(self, channel_data: dict, videos: list):
        self.channel = channel_data
        self.videos = videos
        self.classified_videos = []
        self.metrics_stats = {}
        self.trend_data = {}
        self.algorithm_insights = {}

    def analyze(self) -> dict:
        """종합 분석 수행"""
        if not self.videos:
            return {'error': '분석할 영상이 없습니다'}

        # 0. 조회 속도 및 기본 지표 계산
        self._calculate_view_velocity()
        self._calculate_metrics_stats()

        # 1. YouTube 알고리즘 기반 영상 분류
        self._classify_videos_by_algorithm()

        # 2. 트렌드 분석 (최근 vs 과거)
        self.trend_data = self._analyze_trends()

        # 3. 성공/실패 패턴 분석
        success_analysis = self._analyze_successful_videos()
        failure_analysis = self._analyze_unsuccessful_videos()

        # 4. 콘텐츠 패턴 분석
        content_patterns = self._analyze_content_patterns()

        # 5. 업로드 패턴 분석
        upload_patterns = self._analyze_upload_patterns()

        # 6. 성장 추세 분석
        growth_trends = self._analyze_growth_trends()

        # 7. YouTube 알고리즘 인사이트
        self.algorithm_insights = self._generate_algorithm_insights()

        # 8. 데이터 기반 개선사항 생성
        recommendations = self._generate_data_driven_recommendations(
            success_analysis, failure_analysis, content_patterns,
            upload_patterns, self.trend_data
        )

        # 9. 상세 지표 분석
        detailed_metrics = self._generate_detailed_metrics()

        return {
            'channel_summary': self._get_channel_summary(),
            'video_classification': {
                'viral': [v for v in self.classified_videos if v['classification'] == 'viral'],
                'hit': [v for v in self.classified_videos if v['classification'] == 'hit'],
                'average': [v for v in self.classified_videos if v['classification'] == 'average'],
                'underperform': [v for v in self.classified_videos if v['classification'] == 'underperform'],
            },
            'classification_stats': self._get_classification_stats(),
            'success_analysis': success_analysis,
            'failure_analysis': failure_analysis,
            'content_patterns': content_patterns,
            'upload_patterns': upload_patterns,
            'growth_trends': growth_trends,
            'trend_analysis': self.trend_data,
            'algorithm_insights': self.algorithm_insights,
            'detailed_metrics': detailed_metrics,
            'recommendations': recommendations,
            'metrics_stats': self.metrics_stats,
            'youtube_benchmarks': self.YOUTUBE_BENCHMARKS,
            'analyzed_at': datetime.now().isoformat(),
        }

    def _calculate_view_velocity(self):
        """조회 속도 계산 (업로드 후 일평균 조회수)"""
        now = datetime.now()

        for video in self.videos:
            published = video.get('published_at', '')
            view_count = video.get('view_count', 0)

            if published:
                try:
                    pub_date = datetime.fromisoformat(published.replace('Z', '+00:00'))
                    days_since_upload = max(1, (now - pub_date.replace(tzinfo=None)).days)
                    video['view_velocity'] = round(view_count / days_since_upload, 1)
                    video['days_since_upload'] = days_since_upload
                except:
                    video['view_velocity'] = view_count
                    video['days_since_upload'] = 1
            else:
                video['view_velocity'] = view_count
                video['days_since_upload'] = 1

    def _calculate_metrics_stats(self):
        """각 지표별 통계 계산"""
        if len(self.videos) < 2:
            return

        # 기본 지표
        metrics = ['view_count', 'like_count', 'comment_count', 'view_velocity']

        for metric in metrics:
            values = [v.get(metric, 0) for v in self.videos]
            if values:
                self.metrics_stats[metric] = {
                    'mean': statistics.mean(values),
                    'median': statistics.median(values),
                    'stdev': statistics.stdev(values) if len(values) > 1 else 0,
                    'max': max(values),
                    'min': min(values),
                    'total': sum(values),
                }

        # 참여율 통계
        engagement_rates = []
        like_ratios = []
        comment_rates = []

        for v in self.videos:
            views = v.get('view_count', 0)
            likes = v.get('like_count', 0)
            comments = v.get('comment_count', 0)

            if views > 0:
                engagement_rates.append((likes + comments) / views * 100)
                like_ratios.append(likes / views * 100)
                comment_rates.append(comments / views * 100)

        for name, values in [('engagement_rate', engagement_rates),
                            ('like_ratio', like_ratios),
                            ('comment_rate', comment_rates)]:
            if values:
                self.metrics_stats[name] = {
                    'mean': statistics.mean(values),
                    'median': statistics.median(values),
                    'stdev': statistics.stdev(values) if len(values) > 1 else 0,
                    'max': max(values),
                    'min': min(values),
                }

    def _calculate_title_ctr_score(self, title: str) -> dict:
        """제목 CTR 점수 계산 (0-100)"""
        score = 50  # 기본 점수
        factors = []

        # 1. 제목 길이 (30-50자가 최적)
        length = len(title)
        if 30 <= length <= 50:
            score += 10
            factors.append(f'최적 길이 ({length}자)')
        elif 20 <= length <= 60:
            score += 5
        elif length < 15:
            score -= 10
            factors.append(f'제목 너무 짧음 ({length}자)')
        elif length > 70:
            score -= 5
            factors.append(f'제목 다소 김 ({length}자)')

        # 2. CTR 부스트 키워드 체크
        for category, keywords in self.CTR_BOOST_KEYWORDS.items():
            for kw in keywords:
                if re.search(kw, title, re.IGNORECASE):
                    if category == 'curiosity':
                        score += 8
                        factors.append('호기심 유발 키워드')
                    elif category == 'numbers':
                        score += 7
                        factors.append('숫자 활용')
                    elif category == 'urgency':
                        score += 5
                        factors.append('긴급성 키워드')
                    elif category == 'value':
                        score += 6
                        factors.append('가치 제안 키워드')
                    elif category == 'emotion':
                        score += 7
                        factors.append('감정 유발 키워드')
                    elif category == 'question':
                        score += 5
                        factors.append('질문형 제목')
                    break  # 카테고리당 하나만 카운트

        # 3. 이모지 사용
        if re.search(r'[\U0001F300-\U0001F9FF]', title):
            score += 3
            factors.append('이모지 사용')

        # 4. 대괄호/꺾쇠 사용 (태그 효과)
        if re.search(r'[\[\]【】\(\)]', title):
            score += 4
            factors.append('강조 괄호 사용')

        # 5. 특수문자 과다 사용 체크 (페널티)
        special_count = len(re.findall(r'[!?]{2,}', title))
        if special_count > 2:
            score -= 5
            factors.append('특수문자 과다')

        return {
            'score': min(100, max(0, score)),
            'factors': factors,
            'length': length,
        }

    def _classify_videos_by_algorithm(self):
        """YouTube 알고리즘 기반 영상 분류"""
        if len(self.videos) < 3:
            for video in self.videos:
                video['classification'] = 'average'
                video['algorithm_score'] = 50
                video['score_breakdown'] = {}
            self.classified_videos = self.videos
            return

        # 각 영상별 알고리즘 점수 계산
        for video in self.videos:
            scores = self._calculate_algorithm_score(video)
            video['score_breakdown'] = scores
            video['algorithm_score'] = scores['total']
            video['engagement_rate'] = scores.get('engagement_rate_raw', 0)
            video['like_ratio'] = scores.get('like_ratio_raw', 0)
            video['comment_rate'] = scores.get('comment_rate_raw', 0)
            video['title_analysis'] = scores.get('title_analysis', {})

        # 알고리즘 점수 기준으로 분류
        all_scores = [v['algorithm_score'] for v in self.videos]
        mean_score = statistics.mean(all_scores)
        stdev_score = statistics.stdev(all_scores) if len(all_scores) > 1 else 0

        for video in self.videos:
            score = video['algorithm_score']

            if stdev_score > 0:
                z_score = (score - mean_score) / stdev_score
            else:
                z_score = 0

            video['z_score'] = round(z_score, 2)

            # YouTube 알고리즘 기반 분류
            # 바이럴: Z-score > 1.5 또는 조회속도가 평균의 3배 이상
            view_velocity_avg = self.metrics_stats.get('view_velocity', {}).get('mean', 0)

            if z_score > 1.5 or (view_velocity_avg > 0 and video['view_velocity'] > view_velocity_avg * 3):
                video['classification'] = 'viral'
                video['algorithm_status'] = '알고리즘 추천 가능성 높음'
            elif z_score > 0.5 or (view_velocity_avg > 0 and video['view_velocity'] > view_velocity_avg * 1.5):
                video['classification'] = 'hit'
                video['algorithm_status'] = '좋은 성과'
            elif z_score >= -0.5:
                video['classification'] = 'average'
                video['algorithm_status'] = '평균 성과'
            else:
                video['classification'] = 'underperform'
                video['algorithm_status'] = '개선 필요'

        self.classified_videos = sorted(
            self.videos,
            key=lambda x: x['algorithm_score'],
            reverse=True
        )

    def _calculate_algorithm_score(self, video: dict) -> dict:
        """YouTube 알고리즘 기반 성과 점수 계산"""
        scores = {}

        views = video.get('view_count', 0)
        likes = video.get('like_count', 0)
        comments = video.get('comment_count', 0)
        view_velocity = video.get('view_velocity', 0)
        duration = video.get('duration', '0:00')

        # 1. 조회 속도 점수 (가장 중요!)
        vv_stats = self.metrics_stats.get('view_velocity', {})
        if vv_stats.get('stdev', 0) > 0:
            vv_z = (view_velocity - vv_stats['mean']) / vv_stats['stdev']
            scores['view_velocity'] = min(100, max(0, 50 + vv_z * 20))
        else:
            scores['view_velocity'] = 50
        scores['view_velocity_raw'] = view_velocity

        # 2. 참여율 점수
        if views > 0:
            engagement_rate = (likes + comments) / views * 100
            scores['engagement_rate_raw'] = round(engagement_rate, 3)

            # 벤치마크 기반 점수
            bench = self.YOUTUBE_BENCHMARKS['engagement_rate']
            if engagement_rate >= bench['excellent']:
                scores['engagement_rate'] = 95
            elif engagement_rate >= bench['good']:
                scores['engagement_rate'] = 75
            elif engagement_rate >= bench['average']:
                scores['engagement_rate'] = 55
            elif engagement_rate >= bench['poor']:
                scores['engagement_rate'] = 35
            else:
                scores['engagement_rate'] = 20
        else:
            scores['engagement_rate'] = 0
            scores['engagement_rate_raw'] = 0

        # 3. 좋아요 비율 점수 (만족도 신호)
        if views > 0:
            like_ratio = likes / views * 100
            scores['like_ratio_raw'] = round(like_ratio, 3)

            bench = self.YOUTUBE_BENCHMARKS['like_ratio']
            if like_ratio >= bench['excellent']:
                scores['like_ratio'] = 95
            elif like_ratio >= bench['good']:
                scores['like_ratio'] = 75
            elif like_ratio >= bench['average']:
                scores['like_ratio'] = 55
            elif like_ratio >= bench['poor']:
                scores['like_ratio'] = 35
            else:
                scores['like_ratio'] = 20
        else:
            scores['like_ratio'] = 0
            scores['like_ratio_raw'] = 0

        # 4. 댓글율 점수
        if views > 0:
            comment_rate = comments / views * 100
            scores['comment_rate_raw'] = round(comment_rate, 3)

            bench = self.YOUTUBE_BENCHMARKS['comment_rate']
            if comment_rate >= bench['excellent']:
                scores['comment_rate'] = 95
            elif comment_rate >= bench['good']:
                scores['comment_rate'] = 75
            elif comment_rate >= bench['average']:
                scores['comment_rate'] = 55
            elif comment_rate >= bench['poor']:
                scores['comment_rate'] = 35
            else:
                scores['comment_rate'] = 20
        else:
            scores['comment_rate'] = 0
            scores['comment_rate_raw'] = 0

        # 5. 제목 CTR 점수
        title = video.get('title', '')
        title_analysis = self._calculate_title_ctr_score(title)
        scores['title_ctr_score'] = title_analysis['score']
        scores['title_analysis'] = title_analysis

        # 6. 영상 길이 대비 효율 점수
        duration_seconds = self._duration_to_seconds(duration)
        if duration_seconds > 0 and views > 0:
            # 1분당 조회수
            views_per_minute = views / (duration_seconds / 60)
            vpm_stats = self._calculate_views_per_minute_stats()

            if vpm_stats.get('stdev', 0) > 0:
                vpm_z = (views_per_minute - vpm_stats['mean']) / vpm_stats['stdev']
                scores['duration_efficiency'] = min(100, max(0, 50 + vpm_z * 15))
            else:
                scores['duration_efficiency'] = 50
            scores['views_per_minute'] = round(views_per_minute, 1)
        else:
            scores['duration_efficiency'] = 50
            scores['views_per_minute'] = 0

        # 가중치 적용 총점
        total = 0
        for metric, weight in self.SCORE_WEIGHTS.items():
            total += scores.get(metric, 50) * weight

        scores['total'] = round(total, 1)

        return scores

    def _calculate_views_per_minute_stats(self) -> dict:
        """분당 조회수 통계 계산"""
        vpm_values = []
        for v in self.videos:
            duration = self._duration_to_seconds(v.get('duration', '0:00'))
            views = v.get('view_count', 0)
            if duration > 0 and views > 0:
                vpm_values.append(views / (duration / 60))

        if vpm_values:
            return {
                'mean': statistics.mean(vpm_values),
                'stdev': statistics.stdev(vpm_values) if len(vpm_values) > 1 else 0,
            }
        return {'mean': 0, 'stdev': 0}

    def _duration_to_seconds(self, duration_str: str) -> int:
        """영상 길이를 초로 변환"""
        if not duration_str:
            return 0
        parts = str(duration_str).split(':')
        if len(parts) == 3:
            return int(parts[0]) * 3600 + int(parts[1]) * 60 + int(parts[2])
        elif len(parts) == 2:
            return int(parts[0]) * 60 + int(parts[1])
        return 0

    def _analyze_trends(self) -> dict:
        """최근 vs 과거 트렌드 분석"""
        if len(self.videos) < 10:
            return {'message': '트렌드 분석을 위한 영상이 부족합니다 (최소 10개 필요)'}

        sorted_videos = sorted(
            self.videos,
            key=lambda x: x.get('published_at', ''),
            reverse=True
        )

        mid = len(sorted_videos) // 2
        recent = sorted_videos[:mid]
        older = sorted_videos[mid:]

        trends = {}

        # 1. 조회 속도 트렌드 (핵심!)
        recent_vv = statistics.mean([v['view_velocity'] for v in recent])
        older_vv = statistics.mean([v['view_velocity'] for v in older])
        vv_change = ((recent_vv - older_vv) / older_vv * 100) if older_vv > 0 else 0
        trends['view_velocity'] = {
            'recent_avg': round(recent_vv, 1),
            'older_avg': round(older_vv, 1),
            'change_percent': round(vv_change, 1),
            'trend': '상승' if vv_change > 10 else '하락' if vv_change < -10 else '유지',
            'interpretation': self._interpret_velocity_trend(vv_change),
        }

        # 2. 조회수 트렌드
        recent_views = statistics.mean([v['view_count'] for v in recent])
        older_views = statistics.mean([v['view_count'] for v in older])
        views_change = ((recent_views - older_views) / older_views * 100) if older_views > 0 else 0
        trends['views'] = {
            'recent_avg': round(recent_views),
            'older_avg': round(older_views),
            'change_percent': round(views_change, 1),
            'trend': '상승' if views_change > 10 else '하락' if views_change < -10 else '유지',
        }

        # 3. 참여율 트렌드
        def calc_engagement(videos):
            rates = []
            for v in videos:
                if v['view_count'] > 0:
                    rate = (v['like_count'] + v['comment_count']) / v['view_count'] * 100
                    rates.append(rate)
            return statistics.mean(rates) if rates else 0

        recent_eng = calc_engagement(recent)
        older_eng = calc_engagement(older)
        eng_change = ((recent_eng - older_eng) / older_eng * 100) if older_eng > 0 else 0
        trends['engagement'] = {
            'recent_avg': round(recent_eng, 3),
            'older_avg': round(older_eng, 3),
            'change_percent': round(eng_change, 1),
            'trend': '상승' if eng_change > 10 else '하락' if eng_change < -10 else '유지',
            'benchmark_status': self._get_benchmark_status('engagement_rate', recent_eng),
        }

        # 4. 좋아요 비율 트렌드
        def calc_like_ratio(videos):
            ratios = []
            for v in videos:
                if v['view_count'] > 0:
                    ratios.append(v['like_count'] / v['view_count'] * 100)
            return statistics.mean(ratios) if ratios else 0

        recent_like = calc_like_ratio(recent)
        older_like = calc_like_ratio(older)
        like_change = ((recent_like - older_like) / older_like * 100) if older_like > 0 else 0
        trends['like_ratio'] = {
            'recent_avg': round(recent_like, 3),
            'older_avg': round(older_like, 3),
            'change_percent': round(like_change, 1),
            'trend': '상승' if like_change > 10 else '하락' if like_change < -10 else '유지',
            'benchmark_status': self._get_benchmark_status('like_ratio', recent_like),
        }

        # 5. 제목 길이 트렌드
        recent_title_len = statistics.mean([len(v['title']) for v in recent])
        older_title_len = statistics.mean([len(v['title']) for v in older])
        title_change = recent_title_len - older_title_len
        trends['title_length'] = {
            'recent_avg': round(recent_title_len, 1),
            'older_avg': round(older_title_len, 1),
            'change': round(title_change, 1),
            'trend': '증가' if title_change > 3 else '감소' if title_change < -3 else '유지',
            'optimal_range': '30-50자 권장',
        }

        # 6. 제목 CTR 점수 트렌드
        recent_ctr = statistics.mean([
            self._calculate_title_ctr_score(v['title'])['score'] for v in recent
        ])
        older_ctr = statistics.mean([
            self._calculate_title_ctr_score(v['title'])['score'] for v in older
        ])
        ctr_change = recent_ctr - older_ctr
        trends['title_ctr_score'] = {
            'recent_avg': round(recent_ctr, 1),
            'older_avg': round(older_ctr, 1),
            'change': round(ctr_change, 1),
            'trend': '개선' if ctr_change > 5 else '악화' if ctr_change < -5 else '유지',
        }

        # 7. 댓글 수 트렌드
        recent_comments = statistics.mean([v['comment_count'] for v in recent])
        older_comments = statistics.mean([v['comment_count'] for v in older])
        comment_change = ((recent_comments - older_comments) / older_comments * 100) if older_comments > 0 else 0
        trends['comments'] = {
            'recent_avg': round(recent_comments, 1),
            'older_avg': round(older_comments, 1),
            'change_percent': round(comment_change, 1),
            'trend': '상승' if comment_change > 10 else '하락' if comment_change < -10 else '유지',
        }

        # 8. 성공률 변화
        recent_success = len([v for v in recent if v['classification'] in ['viral', 'hit']]) / len(recent) * 100
        older_success = len([v for v in older if v['classification'] in ['viral', 'hit']]) / len(older) * 100
        trends['success_rate'] = {
            'recent': round(recent_success, 1),
            'older': round(older_success, 1),
            'change': round(recent_success - older_success, 1),
            'trend': '개선' if recent_success > older_success + 5 else '악화' if recent_success < older_success - 5 else '유지',
        }

        return trends

    def _interpret_velocity_trend(self, change_percent: float) -> str:
        """조회 속도 트렌드 해석"""
        if change_percent > 30:
            return '급성장 중! 알고리즘 추천 가능성 높아지고 있음'
        elif change_percent > 10:
            return '성장세 - 현재 전략 유지 권장'
        elif change_percent > -10:
            return '안정적 유지 중'
        elif change_percent > -30:
            return '하락세 - 콘텐츠/썸네일 점검 필요'
        else:
            return '급하락 - 즉각적인 전략 수정 필요'

    def _get_benchmark_status(self, metric: str, value: float) -> str:
        """벤치마크 대비 상태"""
        bench = self.YOUTUBE_BENCHMARKS.get(metric, {})
        if not bench:
            return '데이터 없음'

        if value >= bench.get('excellent', float('inf')):
            return '최상위 (상위 10%)'
        elif value >= bench.get('good', float('inf')):
            return '우수 (상위 30%)'
        elif value >= bench.get('average', float('inf')):
            return '평균'
        elif value >= bench.get('poor', float('inf')):
            return '개선 필요'
        else:
            return '심각한 개선 필요'

    def _generate_algorithm_insights(self) -> dict:
        """YouTube 알고리즘 인사이트 생성"""
        insights = {
            'overall_health': '',
            'algorithm_signals': [],
            'improvement_priorities': [],
            'benchmark_comparison': {},
        }

        # 전체 건강도 평가
        avg_score = statistics.mean([v['algorithm_score'] for v in self.videos])
        if avg_score >= 70:
            insights['overall_health'] = '우수 - 알고리즘 친화적 채널'
        elif avg_score >= 50:
            insights['overall_health'] = '보통 - 개선 여지 있음'
        else:
            insights['overall_health'] = '개선 필요 - 핵심 지표 점검 필요'

        # 알고리즘 신호 분석
        stats = self.metrics_stats

        # 참여율 신호
        eng_avg = stats.get('engagement_rate', {}).get('mean', 0)
        bench = self.YOUTUBE_BENCHMARKS['engagement_rate']
        if eng_avg >= bench['good']:
            insights['algorithm_signals'].append({
                'signal': '참여율',
                'status': 'positive',
                'message': f'참여율 {eng_avg:.2f}%로 우수 (기준: {bench["good"]}% 이상)',
            })
        elif eng_avg < bench['average']:
            insights['algorithm_signals'].append({
                'signal': '참여율',
                'status': 'negative',
                'message': f'참여율 {eng_avg:.2f}%로 낮음 (권장: {bench["average"]}% 이상)',
            })

        # 좋아요 비율 신호
        like_avg = stats.get('like_ratio', {}).get('mean', 0)
        bench = self.YOUTUBE_BENCHMARKS['like_ratio']
        if like_avg >= bench['good']:
            insights['algorithm_signals'].append({
                'signal': '만족도(좋아요 비율)',
                'status': 'positive',
                'message': f'좋아요 비율 {like_avg:.2f}%로 높은 만족도 (기준: {bench["good"]}% 이상)',
            })
        elif like_avg < bench['average']:
            insights['algorithm_signals'].append({
                'signal': '만족도(좋아요 비율)',
                'status': 'negative',
                'message': f'좋아요 비율 {like_avg:.2f}%로 낮음 - 콘텐츠 품질 점검 필요',
            })

        # 개선 우선순위 결정
        priorities = []

        if eng_avg < bench['average']:
            priorities.append({
                'priority': 1,
                'area': '참여율 향상',
                'current': f'{eng_avg:.2f}%',
                'target': f'{bench["good"]}%',
                'actions': ['영상 끝 CTA 강화', '댓글 질문으로 참여 유도', '커뮤니티 탭 활용'],
            })

        like_bench = self.YOUTUBE_BENCHMARKS['like_ratio']
        if like_avg < like_bench['average']:
            priorities.append({
                'priority': 2,
                'area': '좋아요 비율 향상',
                'current': f'{like_avg:.2f}%',
                'target': f'{like_bench["good"]}%',
                'actions': ['콘텐츠 품질 향상', '시청자 기대 충족', '영상 중간 좋아요 요청'],
            })

        # 제목 CTR 분석
        avg_ctr_score = statistics.mean([
            self._calculate_title_ctr_score(v['title'])['score'] for v in self.videos
        ])
        if avg_ctr_score < 60:
            priorities.append({
                'priority': 3,
                'area': '제목 최적화',
                'current': f'{avg_ctr_score:.0f}점',
                'target': '70점 이상',
                'actions': ['호기심 유발 키워드 사용', '숫자 활용', '30-50자 제목 길이 유지'],
            })

        insights['improvement_priorities'] = sorted(priorities, key=lambda x: x['priority'])

        # 벤치마크 비교
        insights['benchmark_comparison'] = {
            'engagement_rate': {
                'current': round(eng_avg, 2),
                'benchmark': self.YOUTUBE_BENCHMARKS['engagement_rate'],
                'status': self._get_benchmark_status('engagement_rate', eng_avg),
            },
            'like_ratio': {
                'current': round(like_avg, 2),
                'benchmark': self.YOUTUBE_BENCHMARKS['like_ratio'],
                'status': self._get_benchmark_status('like_ratio', like_avg),
            },
        }

        return insights

    def _get_channel_summary(self) -> dict:
        """채널 요약 정보"""
        total_views = sum(v['view_count'] for v in self.videos)
        total_likes = sum(v['like_count'] for v in self.videos)
        total_comments = sum(v['comment_count'] for v in self.videos)
        avg_velocity = statistics.mean([v['view_velocity'] for v in self.videos])

        # 평균 지표
        avg_engagement = self.metrics_stats.get('engagement_rate', {}).get('mean', 0)
        avg_like_ratio = self.metrics_stats.get('like_ratio', {}).get('mean', 0)

        return {
            'channel_name': self.channel.get('channel_name'),
            'subscriber_count': self.channel.get('subscriber_count', 0),
            'total_videos_analyzed': len(self.videos),
            'total_views': total_views,
            'total_likes': total_likes,
            'total_comments': total_comments,
            'avg_views_per_video': round(total_views / len(self.videos)) if self.videos else 0,
            'avg_likes_per_video': round(total_likes / len(self.videos)) if self.videos else 0,
            'avg_comments_per_video': round(total_comments / len(self.videos)) if self.videos else 0,
            'avg_view_velocity': round(avg_velocity, 1),
            'avg_engagement_rate': round(avg_engagement, 3),
            'avg_like_ratio': round(avg_like_ratio, 3),
            'engagement_benchmark_status': self._get_benchmark_status('engagement_rate', avg_engagement),
            'like_ratio_benchmark_status': self._get_benchmark_status('like_ratio', avg_like_ratio),
        }

    def _get_classification_stats(self) -> dict:
        """분류별 상세 통계"""
        stats = {
            'viral': {'count': 0, 'avg_views': 0, 'avg_velocity': 0, 'avg_engagement': 0, 'avg_score': 0, 'videos': []},
            'hit': {'count': 0, 'avg_views': 0, 'avg_velocity': 0, 'avg_engagement': 0, 'avg_score': 0, 'videos': []},
            'average': {'count': 0, 'avg_views': 0, 'avg_velocity': 0, 'avg_engagement': 0, 'avg_score': 0, 'videos': []},
            'underperform': {'count': 0, 'avg_views': 0, 'avg_velocity': 0, 'avg_engagement': 0, 'avg_score': 0, 'videos': []},
        }

        for video in self.classified_videos:
            cls = video['classification']
            stats[cls]['count'] += 1
            stats[cls]['videos'].append({
                'video_id': video['video_id'],
                'title': video['title'],
                'thumbnail_url': video.get('thumbnail_url', ''),
                'view_count': video['view_count'],
                'like_count': video.get('like_count', 0),
                'comment_count': video.get('comment_count', 0),
                'view_velocity': video.get('view_velocity', 0),
                'days_since_upload': video.get('days_since_upload', 0),
                'algorithm_score': video['algorithm_score'],
                'engagement_rate': video.get('engagement_rate', 0),
                'like_ratio': video.get('like_ratio', 0),
                'score_breakdown': video.get('score_breakdown', {}),
                'title_analysis': video.get('title_analysis', {}),
                'algorithm_status': video.get('algorithm_status', ''),
            })

        for cls in stats:
            if stats[cls]['count'] > 0:
                videos = stats[cls]['videos']
                stats[cls]['avg_views'] = round(sum(v['view_count'] for v in videos) / len(videos))
                stats[cls]['avg_velocity'] = round(sum(v['view_velocity'] for v in videos) / len(videos), 1)
                stats[cls]['avg_engagement'] = round(sum(v['engagement_rate'] for v in videos) / len(videos), 3)
                stats[cls]['avg_score'] = round(sum(v['algorithm_score'] for v in videos) / len(videos), 1)

        return stats

    def _analyze_successful_videos(self) -> dict:
        """성공 영상 심층 분석"""
        successful = [v for v in self.classified_videos if v['classification'] in ['viral', 'hit']]

        if not successful:
            return {'message': '성공한 영상이 없습니다', 'patterns': [], 'top_videos': []}

        title_analysis = self._analyze_title_patterns(successful)
        duration_analysis = self._analyze_duration_patterns(successful)
        tag_analysis = self._analyze_tags(successful)
        upload_time_analysis = self._analyze_upload_times(successful)

        # 성공 영상 공통점 분석
        common_factors = self._find_success_common_factors(successful)

        top_videos = []
        for video in successful[:7]:
            breakdown = video.get('score_breakdown', {})
            top_videos.append({
                'video_id': video['video_id'],
                'title': video['title'],
                'thumbnail_url': video.get('thumbnail_url', ''),
                'view_count': video['view_count'],
                'view_velocity': video.get('view_velocity', 0),
                'like_count': video.get('like_count', 0),
                'comment_count': video.get('comment_count', 0),
                'engagement_rate': video.get('engagement_rate', 0),
                'like_ratio': video.get('like_ratio', 0),
                'classification': video['classification'],
                'algorithm_score': video['algorithm_score'],
                'score_breakdown': breakdown,
                'title_analysis': video.get('title_analysis', {}),
                'success_reasons': self._analyze_video_success_reasons(video),
            })

        patterns = self._extract_success_patterns(successful, title_analysis, duration_analysis)

        return {
            'total_count': len(successful),
            'avg_views': round(sum(v['view_count'] for v in successful) / len(successful)),
            'avg_velocity': round(sum(v.get('view_velocity', 0) for v in successful) / len(successful), 1),
            'avg_engagement': round(sum(v.get('engagement_rate', 0) for v in successful) / len(successful), 3),
            'avg_like_ratio': round(sum(v.get('like_ratio', 0) for v in successful) / len(successful), 3),
            'avg_score': round(sum(v['algorithm_score'] for v in successful) / len(successful), 1),
            'title_patterns': title_analysis,
            'duration_analysis': duration_analysis,
            'tag_analysis': tag_analysis,
            'upload_time_analysis': upload_time_analysis,
            'common_factors': common_factors,
            'top_videos': top_videos,
            'success_patterns': patterns,
        }

    def _find_success_common_factors(self, successful: list) -> list:
        """성공 영상 공통 요소 분석"""
        factors = []

        # 제목 길이 분석
        avg_title_len = statistics.mean([len(v['title']) for v in successful])
        factors.append({
            'factor': '제목 길이',
            'value': f'{avg_title_len:.0f}자',
            'insight': '최적 범위' if 30 <= avg_title_len <= 50 else '조정 고려',
        })

        # 조회 속도 분석
        avg_velocity = statistics.mean([v.get('view_velocity', 0) for v in successful])
        factors.append({
            'factor': '평균 조회 속도',
            'value': f'{avg_velocity:.0f}회/일',
            'insight': '높은 초기 관심도' if avg_velocity > 1000 else '꾸준한 성장',
        })

        # 참여율 분석
        avg_engagement = statistics.mean([v.get('engagement_rate', 0) for v in successful])
        bench_status = self._get_benchmark_status('engagement_rate', avg_engagement)
        factors.append({
            'factor': '평균 참여율',
            'value': f'{avg_engagement:.2f}%',
            'insight': bench_status,
        })

        # 좋아요 비율 분석
        avg_like = statistics.mean([v.get('like_ratio', 0) for v in successful])
        factors.append({
            'factor': '평균 좋아요 비율',
            'value': f'{avg_like:.2f}%',
            'insight': '높은 만족도' if avg_like >= 3 else '보통 만족도',
        })

        # 제목 CTR 점수 분석
        avg_ctr = statistics.mean([v.get('title_analysis', {}).get('score', 50) for v in successful])
        factors.append({
            'factor': '제목 CTR 점수',
            'value': f'{avg_ctr:.0f}/100',
            'insight': 'CTR 최적화됨' if avg_ctr >= 70 else 'CTR 개선 여지 있음',
        })

        return factors

    def _analyze_unsuccessful_videos(self) -> dict:
        """저조 영상 심층 분석"""
        unsuccessful = [v for v in self.classified_videos if v['classification'] == 'underperform']

        if not unsuccessful:
            return {'message': '저조한 영상이 없습니다', 'patterns': [], 'bottom_videos': []}

        title_analysis = self._analyze_title_patterns(unsuccessful)
        duration_analysis = self._analyze_duration_patterns(unsuccessful)
        tag_analysis = self._analyze_tags(unsuccessful)

        successful = [v for v in self.classified_videos if v['classification'] in ['viral', 'hit']]
        comparison = self._compare_success_vs_failure(successful, unsuccessful) if successful else {}

        bottom_videos = []
        for video in unsuccessful[:7]:
            breakdown = video.get('score_breakdown', {})
            bottom_videos.append({
                'video_id': video['video_id'],
                'title': video['title'],
                'thumbnail_url': video.get('thumbnail_url', ''),
                'view_count': video['view_count'],
                'view_velocity': video.get('view_velocity', 0),
                'like_count': video.get('like_count', 0),
                'comment_count': video.get('comment_count', 0),
                'engagement_rate': video.get('engagement_rate', 0),
                'like_ratio': video.get('like_ratio', 0),
                'classification': video['classification'],
                'algorithm_score': video['algorithm_score'],
                'score_breakdown': breakdown,
                'title_analysis': video.get('title_analysis', {}),
                'failure_reasons': self._analyze_video_failure_reasons(video, comparison),
            })

        patterns = self._extract_failure_patterns(unsuccessful, title_analysis, comparison)

        return {
            'total_count': len(unsuccessful),
            'avg_views': round(sum(v['view_count'] for v in unsuccessful) / len(unsuccessful)),
            'avg_velocity': round(sum(v.get('view_velocity', 0) for v in unsuccessful) / len(unsuccessful), 1),
            'avg_engagement': round(sum(v.get('engagement_rate', 0) for v in unsuccessful) / len(unsuccessful), 3),
            'avg_score': round(sum(v['algorithm_score'] for v in unsuccessful) / len(unsuccessful), 1),
            'title_patterns': title_analysis,
            'duration_analysis': duration_analysis,
            'tag_analysis': tag_analysis,
            'comparison_with_success': comparison,
            'bottom_videos': bottom_videos,
            'failure_patterns': patterns,
        }

    def _compare_success_vs_failure(self, successful: list, unsuccessful: list) -> dict:
        """성공 vs 실패 영상 상세 비교"""
        if not successful or not unsuccessful:
            return {}

        comparison = {}

        # 제목 길이 비교
        success_title_len = statistics.mean([len(v['title']) for v in successful])
        fail_title_len = statistics.mean([len(v['title']) for v in unsuccessful])
        comparison['title_length'] = {
            'success_avg': round(success_title_len, 1),
            'failure_avg': round(fail_title_len, 1),
            'difference': round(success_title_len - fail_title_len, 1),
            'insight': f'성공 영상이 {abs(success_title_len - fail_title_len):.0f}자 {"더 김" if success_title_len > fail_title_len else "더 짧음"}',
        }

        # 조회 속도 비교
        success_vv = statistics.mean([v.get('view_velocity', 0) for v in successful])
        fail_vv = statistics.mean([v.get('view_velocity', 0) for v in unsuccessful])
        comparison['view_velocity'] = {
            'success_avg': round(success_vv, 1),
            'failure_avg': round(fail_vv, 1),
            'difference': round(success_vv - fail_vv, 1),
            'ratio': round(success_vv / fail_vv, 1) if fail_vv > 0 else 0,
            'insight': f'성공 영상이 {success_vv/fail_vv:.1f}배 빠른 조회 속도' if fail_vv > 0 else '',
        }

        # 참여율 비교
        success_eng = statistics.mean([v.get('engagement_rate', 0) for v in successful])
        fail_eng = statistics.mean([v.get('engagement_rate', 0) for v in unsuccessful])
        comparison['engagement_rate'] = {
            'success_avg': round(success_eng, 3),
            'failure_avg': round(fail_eng, 3),
            'difference': round(success_eng - fail_eng, 3),
            'ratio': round(success_eng / fail_eng, 1) if fail_eng > 0 else 0,
        }

        # 좋아요 비율 비교
        success_like = statistics.mean([v.get('like_ratio', 0) for v in successful])
        fail_like = statistics.mean([v.get('like_ratio', 0) for v in unsuccessful])
        comparison['like_ratio'] = {
            'success_avg': round(success_like, 3),
            'failure_avg': round(fail_like, 3),
            'difference': round(success_like - fail_like, 3),
        }

        # 제목 CTR 점수 비교
        success_ctr = statistics.mean([v.get('title_analysis', {}).get('score', 50) for v in successful])
        fail_ctr = statistics.mean([v.get('title_analysis', {}).get('score', 50) for v in unsuccessful])
        comparison['title_ctr_score'] = {
            'success_avg': round(success_ctr, 1),
            'failure_avg': round(fail_ctr, 1),
            'difference': round(success_ctr - fail_ctr, 1),
        }

        # 태그 수 비교
        def avg_tags(videos):
            counts = []
            for v in videos:
                tags = v.get('tags', [])
                if isinstance(tags, str):
                    try:
                        tags = json.loads(tags)
                    except:
                        tags = []
                counts.append(len(tags))
            return statistics.mean(counts) if counts else 0

        comparison['tag_count'] = {
            'success_avg': round(avg_tags(successful), 1),
            'failure_avg': round(avg_tags(unsuccessful), 1),
        }

        return comparison

    def _extract_success_patterns(self, successful: list, title_analysis: dict, duration: dict) -> list:
        """성공 패턴 추출"""
        patterns = []

        # 제목 패턴
        avg_title_len = title_analysis.get('avg_length', 0)
        if 30 <= avg_title_len <= 50:
            patterns.append(f"✓ 최적 제목 길이 유지 (평균 {avg_title_len}자)")
        elif avg_title_len > 50:
            patterns.append(f"상세한 제목으로 정보 전달 (평균 {avg_title_len}자)")

        # 숫자 사용 패턴
        num_pattern = title_analysis.get('patterns', {}).get('has_numbers', 0)
        total = title_analysis.get('total_analyzed', 1)
        if num_pattern / total > 0.4:
            patterns.append(f"✓ 숫자 활용 ({int(num_pattern/total*100)}%) - CTR 향상 효과")

        # 질문형 패턴
        q_pattern = title_analysis.get('patterns', {}).get('has_question', 0)
        if q_pattern / total > 0.25:
            patterns.append(f"✓ 질문형 제목 사용 ({int(q_pattern/total*100)}%) - 호기심 유발")

        # 조회 속도
        avg_velocity = statistics.mean([v.get('view_velocity', 0) for v in successful])
        patterns.append(f"✓ 높은 조회 속도 (평균 {avg_velocity:.0f}회/일)")

        # 참여율
        avg_engagement = statistics.mean([v.get('engagement_rate', 0) for v in successful])
        bench_status = self._get_benchmark_status('engagement_rate', avg_engagement)
        patterns.append(f"✓ 참여율 {avg_engagement:.2f}% ({bench_status})")

        # 좋아요 비율
        avg_like = statistics.mean([v.get('like_ratio', 0) for v in successful])
        if avg_like >= 3:
            patterns.append(f"✓ 높은 좋아요 비율 ({avg_like:.2f}%) - 시청자 만족도 높음")

        return patterns

    def _extract_failure_patterns(self, unsuccessful: list, title_analysis: dict, comparison: dict) -> list:
        """실패 패턴 추출"""
        patterns = []

        # 제목 길이 문제
        title_comp = comparison.get('title_length', {})
        if title_comp:
            diff = title_comp.get('difference', 0)
            if diff > 5:
                patterns.append(f"✗ 제목이 성공 영상 대비 {abs(diff):.0f}자 짧음 - 정보 부족")
            elif diff < -10:
                patterns.append(f"✗ 제목이 성공 영상 대비 {abs(diff):.0f}자 김 - 가독성 저하")

        # 조회 속도 문제
        vv_comp = comparison.get('view_velocity', {})
        if vv_comp and vv_comp.get('ratio', 0) > 2:
            patterns.append(f"✗ 조회 속도가 성공 영상의 {1/vv_comp['ratio']:.0%}에 불과 - 초기 노출 부족")

        # 참여율 문제
        eng_comp = comparison.get('engagement_rate', {})
        if eng_comp:
            diff = eng_comp.get('difference', 0)
            if diff > 1:
                patterns.append(f"✗ 참여율이 성공 영상 대비 {diff:.2f}%p 낮음 - 콘텐츠 매력도 개선 필요")

        # 좋아요 비율 문제
        like_comp = comparison.get('like_ratio', {})
        if like_comp:
            diff = like_comp.get('difference', 0)
            if diff > 1:
                patterns.append(f"✗ 좋아요 비율이 성공 영상 대비 {diff:.2f}%p 낮음 - 시청자 만족도 저조")

        # CTR 점수 문제
        ctr_comp = comparison.get('title_ctr_score', {})
        if ctr_comp and ctr_comp.get('difference', 0) > 10:
            patterns.append(f"✗ 제목 CTR 점수가 {ctr_comp['difference']:.0f}점 낮음 - 제목/썸네일 최적화 필요")

        # 태그 문제
        tag_comp = comparison.get('tag_count', {})
        if tag_comp:
            success_tags = tag_comp.get('success_avg', 0)
            fail_tags = tag_comp.get('failure_avg', 0)
            if success_tags > fail_tags + 3:
                patterns.append(f"✗ 태그 수 부족 (성공: {success_tags:.0f}개 vs 실패: {fail_tags:.0f}개)")

        if not patterns:
            patterns.append("시청자 관심 영역 이탈 또는 경쟁 콘텐츠 대비 차별화 부족")

        return patterns

    def _analyze_video_success_reasons(self, video: dict) -> list:
        """개별 영상 성공 이유 분석"""
        reasons = []
        breakdown = video.get('score_breakdown', {})

        # 조회 속도 기반
        if breakdown.get('view_velocity', 0) > 70:
            reasons.append(f"빠른 조회 속도 ({video.get('view_velocity', 0):.0f}회/일) - 알고리즘 추천 효과")

        # 참여율 기반
        if breakdown.get('engagement_rate', 0) > 70:
            reasons.append(f"높은 참여율 ({breakdown.get('engagement_rate_raw', 0):.2f}%)")

        # 좋아요 비율 기반
        if breakdown.get('like_ratio', 0) > 70:
            reasons.append(f"높은 만족도 (좋아요 {breakdown.get('like_ratio_raw', 0):.2f}%)")

        # 댓글율 기반
        if breakdown.get('comment_rate', 0) > 70:
            reasons.append(f"활발한 댓글 소통 ({breakdown.get('comment_rate_raw', 0):.2f}%)")

        # 제목 분석
        title_analysis = video.get('title_analysis', {})
        if title_analysis.get('score', 0) >= 70:
            factors = title_analysis.get('factors', [])
            if factors:
                reasons.append(f"최적화된 제목 ({', '.join(factors[:2])})")

        if not reasons:
            reasons.append("채널 평균 이상의 종합 성과")

        return reasons

    def _analyze_video_failure_reasons(self, video: dict, comparison: dict) -> list:
        """개별 영상 실패 이유 분석"""
        reasons = []
        breakdown = video.get('score_breakdown', {})

        # 조회 속도 기반
        if breakdown.get('view_velocity', 0) < 30:
            reasons.append(f"낮은 조회 속도 ({video.get('view_velocity', 0):.0f}회/일) - 노출/클릭률 개선 필요")

        # 참여율 기반
        if breakdown.get('engagement_rate', 0) < 30:
            reasons.append(f"낮은 참여율 ({breakdown.get('engagement_rate_raw', 0):.2f}%)")

        # 좋아요 비율 기반
        if breakdown.get('like_ratio', 0) < 30:
            reasons.append(f"낮은 만족도 (좋아요 {breakdown.get('like_ratio_raw', 0):.2f}%)")

        # 제목 CTR 점수 기반
        title_analysis = video.get('title_analysis', {})
        if title_analysis.get('score', 50) < 50:
            reasons.append(f"제목 CTR 점수 낮음 ({title_analysis['score']}점) - 제목 최적화 필요")

        # 성공 영상과 비교
        if comparison:
            success_len = comparison.get('title_length', {}).get('success_avg', 0)
            if success_len and len(video['title']) < success_len - 10:
                reasons.append(f"제목 길이 부족 ({len(video['title'])}자 vs 성공영상 {success_len:.0f}자)")

        # 태그 분석
        tags = video.get('tags', [])
        if isinstance(tags, str):
            try:
                tags = json.loads(tags)
            except:
                tags = []
        if len(tags) < 5:
            reasons.append(f"태그 부족 ({len(tags)}개) - 검색 노출 제한")

        if not reasons:
            reasons.append("시청자 관심 영역 이탈 또는 경쟁 콘텐츠 대비 차별화 부족")

        return reasons

    def _generate_data_driven_recommendations(self, success: dict, failure: dict,
                                              content: dict, upload: dict, trends: dict) -> list:
        """데이터 기반 개선사항 자동 생성"""
        recommendations = []

        # 1. YouTube 알고리즘 인사이트 기반
        if self.algorithm_insights.get('improvement_priorities'):
            priorities = self.algorithm_insights['improvement_priorities']
            for p in priorities[:3]:
                recommendations.append({
                    'category': f"🎯 우선순위 {p['priority']}: {p['area']}",
                    'priority': 'critical' if p['priority'] == 1 else 'high',
                    'current': p['current'],
                    'target': p['target'],
                    'suggestions': p['actions'],
                })

        # 2. 트렌드 기반 추천
        if trends and not trends.get('message'):
            trend_recs = self._generate_trend_recommendations(trends)
            if trend_recs:
                recommendations.append({
                    'category': '📈 트렌드 분석 기반 개선사항',
                    'priority': 'high',
                    'suggestions': trend_recs,
                })

        # 3. 성공 패턴 강화
        if success.get('success_patterns'):
            recommendations.append({
                'category': '✅ 성공 패턴 유지/강화',
                'priority': 'medium',
                'suggestions': success['success_patterns'][:5],
            })

        # 4. 실패 패턴 개선
        if failure.get('failure_patterns'):
            recommendations.append({
                'category': '⚠️ 개선 필요 영역',
                'priority': 'high',
                'suggestions': failure['failure_patterns'][:4],
            })

        # 5. 성공 vs 실패 비교 기반
        comparison = failure.get('comparison_with_success', {})
        if comparison:
            comp_recs = self._generate_comparison_recommendations(comparison)
            if comp_recs:
                recommendations.append({
                    'category': '🎯 성공영상 벤치마크 기반',
                    'priority': 'high',
                    'suggestions': comp_recs,
                })

        # 6. 제목 최적화 추천
        title_recs = self._generate_title_recommendations(success, failure, trends)
        if title_recs:
            recommendations.append({
                'category': '📝 제목 최적화 (CTR 향상)',
                'priority': 'medium',
                'suggestions': title_recs,
            })

        # 7. 업로드 패턴 추천
        if upload and not upload.get('message'):
            upload_recs = self._generate_upload_recommendations(upload)
            if upload_recs:
                recommendations.append({
                    'category': '🗓️ 업로드 전략',
                    'priority': 'medium',
                    'suggestions': upload_recs,
                })

        return recommendations

    def _generate_trend_recommendations(self, trends: dict) -> list:
        """트렌드 기반 추천"""
        recs = []

        # 조회 속도 트렌드 (가장 중요)
        vv_trend = trends.get('view_velocity', {})
        if vv_trend.get('trend') == '상승':
            recs.append(f"✓ 조회 속도 {vv_trend['change_percent']:+.1f}% 성장 - {vv_trend.get('interpretation', '')}")
        elif vv_trend.get('trend') == '하락':
            recs.append(f"✗ 조회 속도 {vv_trend['change_percent']:.1f}% 하락 - {vv_trend.get('interpretation', '')}")

        # 참여율 트렌드
        eng_trend = trends.get('engagement', {})
        if eng_trend.get('trend') == '상승':
            recs.append(f"✓ 참여율 {eng_trend['recent_avg']:.2f}% ({eng_trend.get('benchmark_status', '')})")
        elif eng_trend.get('trend') == '하락':
            recs.append(f"✗ 참여율 하락 {eng_trend['change_percent']:.1f}% - CTA 강화 필요")

        # 제목 CTR 점수 트렌드
        ctr_trend = trends.get('title_ctr_score', {})
        if ctr_trend.get('trend') == '악화':
            recs.append(f"✗ 제목 CTR 점수 하락 ({ctr_trend['older_avg']:.0f} → {ctr_trend['recent_avg']:.0f})")

        # 제목 길이 변화
        title_trend = trends.get('title_length', {})
        if title_trend:
            recs.append(f"제목 길이: {title_trend['older_avg']:.0f}자 → {title_trend['recent_avg']:.0f}자 ({title_trend['optimal_range']})")

        # 성공률 변화
        success_trend = trends.get('success_rate', {})
        if success_trend.get('trend') == '개선':
            recs.append(f"✓ 성공 영상 비율 개선 ({success_trend['older']:.0f}% → {success_trend['recent']:.0f}%)")
        elif success_trend.get('trend') == '악화':
            recs.append(f"✗ 성공 영상 비율 하락 - 콘텐츠 방향성 점검 필요")

        return recs

    def _generate_comparison_recommendations(self, comparison: dict) -> list:
        """성공 vs 실패 비교 기반 추천"""
        recs = []

        vv_comp = comparison.get('view_velocity', {})
        if vv_comp.get('ratio', 0) > 2:
            recs.append(f"초기 24시간 노출 전략 강화 필요 (성공영상 대비 {1/vv_comp['ratio']:.0%} 수준)")

        title_comp = comparison.get('title_length', {})
        if title_comp.get('difference', 0) > 5:
            recs.append(f"제목 길이를 {title_comp['success_avg']:.0f}자 수준으로 조정")

        eng_comp = comparison.get('engagement_rate', {})
        if eng_comp.get('difference', 0) > 1:
            recs.append(f"참여율 목표: {eng_comp['success_avg']:.2f}% (현재 저조영상: {eng_comp['failure_avg']:.2f}%)")

        ctr_comp = comparison.get('title_ctr_score', {})
        if ctr_comp.get('difference', 0) > 10:
            recs.append(f"제목 CTR 점수 향상 필요 (성공: {ctr_comp['success_avg']:.0f}점 vs 실패: {ctr_comp['failure_avg']:.0f}점)")

        return recs

    def _generate_title_recommendations(self, success: dict, failure: dict, trends: dict) -> list:
        """제목 최적화 추천"""
        recs = []

        success_title = success.get('title_patterns', {})
        if success_title:
            success_len = success_title.get('avg_length', 0)
            if success_len > 0:
                recs.append(f"권장 제목 길이: {int(success_len-5)}~{int(success_len+5)}자")

            # 숫자 사용
            success_nums = success_title.get('patterns', {}).get('has_numbers', 0)
            success_total = success_title.get('total_analyzed', 1)
            if success_nums / success_total > 0.3:
                recs.append(f"숫자 활용 권장 - 구체성 강화 (예: 'TOP 5', '3가지 방법')")

        # CTR 부스트 키워드 추천
        recs.append("호기심 유발 키워드 사용: '비밀', '진실', '몰랐던', '실제로'")
        recs.append("가치 제안 키워드 추가: '꿀팁', '핵심', '완벽 가이드'")

        return recs

    def _generate_upload_recommendations(self, upload: dict) -> list:
        """업로드 전략 추천"""
        recs = []

        interval = upload.get('avg_upload_interval_days', 0)
        if interval > 7:
            recs.append(f"업로드 간격 단축 권장 (현재 {interval:.1f}일 → 주 1~2회)")
        elif interval < 2:
            recs.append(f"현재 업로드 빈도 ({interval:.1f}일) 유지 - 꾸준함이 핵심")

        weekday_dist = upload.get('weekday_distribution', {})
        if weekday_dist:
            best_days = sorted(weekday_dist.items(), key=lambda x: x[1], reverse=True)[:2]
            if best_days:
                day_names = {'Monday': '월', 'Tuesday': '화', 'Wednesday': '수',
                           'Thursday': '목', 'Friday': '금', 'Saturday': '토', 'Sunday': '일'}
                days = [day_names.get(d[0], d[0]) for d in best_days]
                recs.append(f"주요 업로드 요일: {', '.join(days)}요일 - 일관성 유지")

        return recs

    def _generate_detailed_metrics(self) -> dict:
        """상세 지표 분석"""
        return {
            'view_velocity_distribution': self._get_velocity_distribution(),
            'engagement_distribution': self._get_engagement_distribution(),
            'performance_score_distribution': self._get_score_distribution(),
            'monthly_performance': self._get_monthly_performance(),
            'title_ctr_distribution': self._get_ctr_distribution(),
        }

    def _get_velocity_distribution(self) -> dict:
        """조회 속도 분포"""
        velocities = [v.get('view_velocity', 0) for v in self.videos]
        if not velocities:
            return {}

        return {
            '0-100': len([v for v in velocities if v < 100]),
            '100-500': len([v for v in velocities if 100 <= v < 500]),
            '500-1000': len([v for v in velocities if 500 <= v < 1000]),
            '1000-5000': len([v for v in velocities if 1000 <= v < 5000]),
            '5000+': len([v for v in velocities if v >= 5000]),
        }

    def _get_engagement_distribution(self) -> dict:
        """참여율 분포"""
        rates = [v.get('engagement_rate', 0) for v in self.videos]
        if not rates:
            return {}

        return {
            '0-1%': len([r for r in rates if r < 1]),
            '1-3%': len([r for r in rates if 1 <= r < 3]),
            '3-5%': len([r for r in rates if 3 <= r < 5]),
            '5-8%': len([r for r in rates if 5 <= r < 8]),
            '8%+': len([r for r in rates if r >= 8]),
        }

    def _get_score_distribution(self) -> dict:
        """알고리즘 점수 분포"""
        scores = [v.get('algorithm_score', 0) for v in self.videos]
        return {
            '0-30 (저조)': len([s for s in scores if s < 30]),
            '30-50 (평균 이하)': len([s for s in scores if 30 <= s < 50]),
            '50-65 (평균)': len([s for s in scores if 50 <= s < 65]),
            '65-80 (우수)': len([s for s in scores if 65 <= s < 80]),
            '80+ (최상위)': len([s for s in scores if s >= 80]),
        }

    def _get_ctr_distribution(self) -> dict:
        """제목 CTR 점수 분포"""
        scores = [v.get('title_analysis', {}).get('score', 50) for v in self.videos]
        return {
            '0-40 (낮음)': len([s for s in scores if s < 40]),
            '40-55 (보통)': len([s for s in scores if 40 <= s < 55]),
            '55-70 (양호)': len([s for s in scores if 55 <= s < 70]),
            '70-85 (우수)': len([s for s in scores if 70 <= s < 85]),
            '85+ (최적)': len([s for s in scores if s >= 85]),
        }

    def _get_monthly_performance(self) -> dict:
        """월별 성과 추이"""
        monthly = defaultdict(lambda: {'views': 0, 'velocity': [], 'count': 0, 'engagement': []})

        for video in self.videos:
            published = video.get('published_at', '')
            if published:
                try:
                    dt = datetime.fromisoformat(published.replace('Z', '+00:00'))
                    month_key = dt.strftime('%Y-%m')
                    monthly[month_key]['views'] += video['view_count']
                    monthly[month_key]['velocity'].append(video.get('view_velocity', 0))
                    monthly[month_key]['count'] += 1
                    if video['view_count'] > 0:
                        eng = (video['like_count'] + video['comment_count']) / video['view_count'] * 100
                        monthly[month_key]['engagement'].append(eng)
                except:
                    pass

        result = {}
        for month, data in sorted(monthly.items())[-6:]:
            result[month] = {
                'avg_views': round(data['views'] / data['count']) if data['count'] > 0 else 0,
                'avg_velocity': round(statistics.mean(data['velocity']), 1) if data['velocity'] else 0,
                'video_count': data['count'],
                'avg_engagement': round(statistics.mean(data['engagement']), 3) if data['engagement'] else 0,
            }

        return result

    # === 기존 헬퍼 메서드들 ===

    def _analyze_title_patterns(self, videos: list) -> dict:
        """제목 패턴 분석"""
        titles = [v['title'] for v in videos]
        lengths = [len(t) for t in titles]

        all_words = []
        for title in titles:
            words = re.findall(r'[가-힣]+|[a-zA-Z]+|\d+', title)
            all_words.extend([w.lower() for w in words if len(w) > 1])

        return {
            'avg_length': round(sum(lengths) / len(lengths)) if lengths else 0,
            'min_length': min(lengths) if lengths else 0,
            'max_length': max(lengths) if lengths else 0,
            'top_words': Counter(all_words).most_common(10),
            'patterns': {
                'has_numbers': sum(1 for t in titles if re.search(r'\d', t)),
                'has_question': sum(1 for t in titles if '?' in t),
                'has_emoji': sum(1 for t in titles if re.search(r'[\U0001F300-\U0001F9FF]', t)),
                'has_brackets': sum(1 for t in titles if '[' in t or '【' in t),
            },
            'total_analyzed': len(titles),
        }

    def _analyze_duration_patterns(self, videos: list) -> dict:
        """영상 길이 패턴"""
        durations = [self._duration_to_seconds(v.get('duration', '0:00')) for v in videos]
        durations = [d for d in durations if d > 0]

        if not durations:
            return {'avg_duration': 0, 'distribution': {}}

        return {
            'avg_duration_seconds': round(sum(durations) / len(durations)),
            'distribution': {
                'shorts (1분 이하)': sum(1 for d in durations if d <= 60),
                'short (1-5분)': sum(1 for d in durations if 60 < d <= 300),
                'medium (5-10분)': sum(1 for d in durations if 300 < d <= 600),
                'long (10-20분)': sum(1 for d in durations if 600 < d <= 1200),
                'very_long (20분+)': sum(1 for d in durations if d > 1200),
            },
        }

    def _analyze_tags(self, videos: list) -> dict:
        """태그 분석"""
        all_tags = []
        videos_with_tags = 0

        for video in videos:
            tags = video.get('tags', [])
            if isinstance(tags, str):
                try:
                    tags = json.loads(tags)
                except:
                    tags = []
            if tags:
                videos_with_tags += 1
            all_tags.extend(tags)

        return {
            'top_tags': Counter(all_tags).most_common(15),
            'avg_tags_per_video': round(len(all_tags) / len(videos)) if videos else 0,
            'videos_with_tags': videos_with_tags,
            'total_unique_tags': len(set(all_tags)),
        }

    def _analyze_upload_times(self, videos: list) -> dict:
        """업로드 시간대 분석"""
        weekdays = Counter()
        hours = Counter()

        for video in videos:
            published = video.get('published_at')
            if published:
                try:
                    dt = datetime.fromisoformat(published.replace('Z', '+00:00'))
                    weekdays[dt.strftime('%A')] += 1
                    hours[dt.hour] += 1
                except:
                    pass

        return {
            'best_weekdays': weekdays.most_common(3),
            'best_hours': hours.most_common(5),
        }

    def _analyze_content_patterns(self) -> dict:
        """콘텐츠 패턴 분석"""
        all_keywords = []
        for video in self.videos:
            title = video.get('title', '')
            keywords = re.findall(r'[가-힣]+', title)
            all_keywords.extend([k for k in keywords if len(k) > 1])

        return {
            'top_keywords': Counter(all_keywords).most_common(20),
            'content_diversity': len(set(all_keywords)) / len(all_keywords) if all_keywords else 0,
        }

    def _analyze_upload_patterns(self) -> dict:
        """업로드 패턴 분석"""
        if len(self.videos) < 2:
            return {'message': '분석할 영상이 부족합니다'}

        dates = []
        for video in self.videos:
            published = video.get('published_at')
            if published:
                try:
                    dt = datetime.fromisoformat(published.replace('Z', '+00:00'))
                    dates.append(dt)
                except:
                    pass

        if len(dates) < 2:
            return {'message': '날짜 데이터 부족'}

        dates.sort(reverse=True)
        intervals = [(dates[i] - dates[i + 1]).days for i in range(len(dates) - 1)]
        avg_interval = sum(intervals) / len(intervals) if intervals else 0

        weekday_dist = Counter(d.strftime('%A') for d in dates)
        monthly_dist = Counter(d.strftime('%Y-%m') for d in dates)

        return {
            'avg_upload_interval_days': round(avg_interval, 1),
            'upload_frequency': (
                '매일' if avg_interval < 2 else
                '주 2-3회' if avg_interval < 4 else
                '주 1회' if avg_interval < 8 else
                '격주' if avg_interval < 15 else '월 1-2회'
            ),
            'weekday_distribution': dict(weekday_dist.most_common()),
            'monthly_distribution': dict(sorted(monthly_dist.items(), reverse=True)[:6]),
            'total_videos_analyzed': len(dates),
        }

    def _analyze_growth_trends(self) -> dict:
        """성장 추세 분석"""
        if len(self.videos) < 5:
            return {'message': '추세 분석을 위한 영상이 부족합니다'}

        sorted_videos = sorted(
            self.videos,
            key=lambda x: x.get('published_at', ''),
            reverse=True
        )

        recent_count = min(10, len(sorted_videos) // 2)
        recent = sorted_videos[:recent_count]
        older = sorted_videos[-recent_count:]

        recent_avg = sum(v['view_count'] for v in recent) / len(recent)
        older_avg = sum(v['view_count'] for v in older) / len(older)
        growth_rate = ((recent_avg - older_avg) / older_avg * 100) if older_avg > 0 else 0

        # 조회 속도 성장
        recent_vv = sum(v.get('view_velocity', 0) for v in recent) / len(recent)
        older_vv = sum(v.get('view_velocity', 0) for v in older) / len(older)
        vv_growth = ((recent_vv - older_vv) / older_vv * 100) if older_vv > 0 else 0

        return {
            'recent_avg_views': round(recent_avg),
            'older_avg_views': round(older_avg),
            'growth_rate_percent': round(growth_rate, 1),
            'recent_avg_velocity': round(recent_vv, 1),
            'older_avg_velocity': round(older_vv, 1),
            'velocity_growth_percent': round(vv_growth, 1),
            'trend': '성장세' if growth_rate > 10 else '유지' if growth_rate > -10 else '하락세',
            'velocity_trend': '가속화' if vv_growth > 10 else '유지' if vv_growth > -10 else '둔화',
            'videos_compared': recent_count * 2,
        }


class CompetitorAnalyzer:
    """경쟁사 비교 분석기 - 상세 분석 버전"""

    def __init__(self, main_channel_analysis: dict, competitor_analyses: list):
        self.main = main_channel_analysis
        self.competitors = competitor_analyses

    def analyze(self) -> dict:
        """경쟁사 비교 분석 - 종합 분석"""
        if not self.competitors:
            return {'error': '비교할 경쟁사가 없습니다'}

        return {
            'main_channel': self._extract_detailed_summary(self.main),
            'competitors': [self._extract_detailed_summary(c) for c in self.competitors],
            'metrics_comparison': self._compare_metrics(),
            'ranking_analysis': self._analyze_rankings(),
            'content_strategy_comparison': self._compare_content_strategy(),
            'performance_gap_analysis': self._analyze_performance_gaps(),
            'strengths_weaknesses': self._analyze_strengths_weaknesses(),
            'market_position': self._analyze_market_position(),
            'competitive_insights': self._generate_competitive_insights(),
            'recommendations': self._generate_competitive_recommendations(),
        }

    def _extract_detailed_summary(self, analysis: dict) -> dict:
        """분석 결과에서 상세 정보 추출"""
        channel_summary = analysis.get('channel_summary', {})
        classification = analysis.get('classification_stats', {})
        success = analysis.get('success_analysis', {})

        viral_videos = classification.get('viral', {}).get('videos', [])
        hit_videos = classification.get('hit', {}).get('videos', [])
        avg_videos = classification.get('average', {}).get('videos', [])
        under_videos = classification.get('underperform', {}).get('videos', [])

        total = len(viral_videos) + len(hit_videos) + len(avg_videos) + len(under_videos)

        return {
            'channel_name': channel_summary.get('channel_name'),
            'channel_id': channel_summary.get('channel_id'),
            'subscriber_count': channel_summary.get('subscriber_count', 0),
            'avg_views': channel_summary.get('avg_views_per_video', 0),
            'avg_velocity': channel_summary.get('avg_view_velocity', 0),
            'avg_engagement': channel_summary.get('avg_engagement_rate', 0),
            'avg_like_ratio': channel_summary.get('avg_like_ratio', 0),
            'total_videos': total,
            'viral_count': len(viral_videos),
            'hit_count': len(hit_videos),
            'average_count': len(avg_videos),
            'underperform_count': len(under_videos),
            'viral_rate': round(len(viral_videos) / total * 100, 1) if total > 0 else 0,
            'hit_rate': round(len(hit_videos) / total * 100, 1) if total > 0 else 0,
            'success_rate': round((len(viral_videos) + len(hit_videos)) / total * 100, 1) if total > 0 else 0,
            'top_video_views': max([v.get('view_count', 0) for v in viral_videos + hit_videos], default=0),
            'success_patterns': success.get('success_patterns', [])[:3],
        }

    def _compare_metrics(self) -> dict:
        """상세 지표 비교"""
        main_summary = self._extract_detailed_summary(self.main)
        comparisons = []

        for comp in self.competitors:
            comp_summary = self._extract_detailed_summary(comp)

            # 비율 계산 (내 채널 대비 경쟁사)
            def safe_ratio(a, b):
                return round(a / b * 100, 1) if b > 0 else 0

            comparisons.append({
                'channel_name': comp_summary['channel_name'],
                'subscriber_count': comp_summary['subscriber_count'],
                'subscriber_diff': main_summary['subscriber_count'] - comp_summary['subscriber_count'],
                'subscriber_ratio': safe_ratio(main_summary['subscriber_count'], comp_summary['subscriber_count']),
                'avg_views': comp_summary['avg_views'],
                'views_diff': main_summary['avg_views'] - comp_summary['avg_views'],
                'views_ratio': safe_ratio(main_summary['avg_views'], comp_summary['avg_views']),
                'avg_velocity': comp_summary['avg_velocity'],
                'velocity_diff': main_summary['avg_velocity'] - comp_summary['avg_velocity'],
                'velocity_ratio': safe_ratio(main_summary['avg_velocity'], comp_summary['avg_velocity']),
                'avg_engagement': comp_summary['avg_engagement'],
                'engagement_diff': round(main_summary['avg_engagement'] - comp_summary['avg_engagement'], 3),
                'viral_rate': comp_summary['viral_rate'],
                'success_rate': comp_summary['success_rate'],
                'success_rate_diff': round(main_summary['success_rate'] - comp_summary['success_rate'], 1),
            })

        return {
            'main_channel': main_summary,
            'comparisons': comparisons,
            'summary': {
                'total_compared': len(comparisons),
                'better_in_views': sum(1 for c in comparisons if c['views_diff'] > 0),
                'better_in_engagement': sum(1 for c in comparisons if c['engagement_diff'] > 0),
                'better_in_viral': sum(1 for c in comparisons if main_summary['viral_rate'] > c['viral_rate']),
            }
        }

    def _analyze_rankings(self) -> dict:
        """전체 순위 분석"""
        main_summary = self._extract_detailed_summary(self.main)
        all_summaries = [main_summary] + [self._extract_detailed_summary(c) for c in self.competitors]
        main_name = main_summary['channel_name']
        total = len(all_summaries)

        metrics = {
            'subscriber_count': '구독자 수',
            'avg_views': '평균 조회수',
            'avg_engagement': '참여율',
            'avg_velocity': '조회 속도',
            'viral_rate': '바이럴 비율',
            'success_rate': '성공률',
        }

        rankings = {}
        for metric, name in metrics.items():
            sorted_list = sorted(all_summaries, key=lambda x: x.get(metric, 0), reverse=True)
            rank = next(i for i, x in enumerate(sorted_list) if x['channel_name'] == main_name) + 1
            top_channel = sorted_list[0]

            rankings[metric] = {
                'name': name,
                'rank': rank,
                'total': total,
                'value': main_summary.get(metric, 0),
                'top_value': top_channel.get(metric, 0),
                'top_channel': top_channel['channel_name'],
                'is_top': rank == 1,
                'gap_to_top': round(top_channel.get(metric, 0) - main_summary.get(metric, 0), 2) if rank > 1 else 0,
            }

        return rankings

    def _compare_content_strategy(self) -> dict:
        """콘텐츠 전략 비교"""
        main_summary = self._extract_detailed_summary(self.main)
        comp_summaries = [self._extract_detailed_summary(c) for c in self.competitors]

        # 전략 유형 분류
        def classify_strategy(summary):
            viral_rate = summary['viral_rate']
            engagement = summary['avg_engagement']

            if viral_rate >= 20:
                return '바이럴 중심'
            elif engagement >= 8:
                return '팬덤 중심'
            elif summary['avg_velocity'] > 1000:
                return '트래픽 중심'
            else:
                return '균형 전략'

        return {
            'main_strategy': classify_strategy(main_summary),
            'competitor_strategies': [
                {
                    'channel_name': s['channel_name'],
                    'strategy': classify_strategy(s),
                    'viral_rate': s['viral_rate'],
                    'engagement': s['avg_engagement'],
                }
                for s in comp_summaries
            ],
            'strategy_distribution': {
                '바이럴 중심': sum(1 for s in comp_summaries if classify_strategy(s) == '바이럴 중심'),
                '팬덤 중심': sum(1 for s in comp_summaries if classify_strategy(s) == '팬덤 중심'),
                '트래픽 중심': sum(1 for s in comp_summaries if classify_strategy(s) == '트래픽 중심'),
                '균형 전략': sum(1 for s in comp_summaries if classify_strategy(s) == '균형 전략'),
            }
        }

    def _analyze_performance_gaps(self) -> dict:
        """성과 격차 분석"""
        main_summary = self._extract_detailed_summary(self.main)
        comp_summaries = [self._extract_detailed_summary(c) for c in self.competitors]

        if not comp_summaries:
            return {}

        # 경쟁사 평균
        avg_subs = sum(c['subscriber_count'] for c in comp_summaries) / len(comp_summaries)
        avg_views = sum(c['avg_views'] for c in comp_summaries) / len(comp_summaries)
        avg_engagement = sum(c['avg_engagement'] for c in comp_summaries) / len(comp_summaries)
        avg_viral_rate = sum(c['viral_rate'] for c in comp_summaries) / len(comp_summaries)

        # 최고 성과자
        best_subs = max(comp_summaries, key=lambda x: x['subscriber_count'])
        best_views = max(comp_summaries, key=lambda x: x['avg_views'])
        best_engagement = max(comp_summaries, key=lambda x: x['avg_engagement'])
        best_viral = max(comp_summaries, key=lambda x: x['viral_rate'])

        return {
            'vs_average': {
                'subscriber_gap': main_summary['subscriber_count'] - avg_subs,
                'subscriber_gap_pct': round((main_summary['subscriber_count'] - avg_subs) / avg_subs * 100, 1) if avg_subs > 0 else 0,
                'views_gap': main_summary['avg_views'] - avg_views,
                'views_gap_pct': round((main_summary['avg_views'] - avg_views) / avg_views * 100, 1) if avg_views > 0 else 0,
                'engagement_gap': round(main_summary['avg_engagement'] - avg_engagement, 2),
                'viral_rate_gap': round(main_summary['viral_rate'] - avg_viral_rate, 1),
            },
            'vs_best': {
                'best_subscriber_channel': best_subs['channel_name'],
                'subscriber_gap_to_best': main_summary['subscriber_count'] - best_subs['subscriber_count'],
                'best_views_channel': best_views['channel_name'],
                'views_gap_to_best': main_summary['avg_views'] - best_views['avg_views'],
                'best_engagement_channel': best_engagement['channel_name'],
                'engagement_gap_to_best': round(main_summary['avg_engagement'] - best_engagement['avg_engagement'], 2),
                'best_viral_channel': best_viral['channel_name'],
                'viral_gap_to_best': round(main_summary['viral_rate'] - best_viral['viral_rate'], 1),
            },
            'competitive_advantages': self._identify_advantages(main_summary, comp_summaries),
        }

    def _identify_advantages(self, main: dict, competitors: list) -> list:
        """경쟁 우위 항목 식별"""
        advantages = []

        for comp in competitors:
            if main['avg_views'] > comp['avg_views'] * 1.2:
                advantages.append(f"{comp['channel_name']} 대비 조회수 우위 (+{round((main['avg_views']/comp['avg_views']-1)*100)}%)")
            if main['avg_engagement'] > comp['avg_engagement'] * 1.2:
                advantages.append(f"{comp['channel_name']} 대비 참여율 우위")
            if main['viral_rate'] > comp['viral_rate'] + 5:
                advantages.append(f"{comp['channel_name']} 대비 바이럴 성공률 우위")

        return advantages[:5]  # 상위 5개만

    def _analyze_strengths_weaknesses(self) -> dict:
        """강점/약점 상세 분석 - 1위와의 격차 기반"""
        main_summary = self._extract_detailed_summary(self.main)
        all_summaries = [main_summary] + [self._extract_detailed_summary(c) for c in self.competitors]
        main_name = main_summary['channel_name']
        total = len(all_summaries)

        # 지표별 키 매핑
        metric_keys = {
            'subscribers': 'subscriber_count',
            'avg_views': 'avg_views',
            'engagement': 'avg_engagement',
            'view_velocity': 'avg_velocity',
            'viral_rate': 'viral_rate',
            'success_rate': 'success_rate',
        }

        rankings = {
            'subscribers': ('구독자 수', sorted(all_summaries, key=lambda x: x['subscriber_count'], reverse=True)),
            'avg_views': ('평균 조회수', sorted(all_summaries, key=lambda x: x['avg_views'], reverse=True)),
            'engagement': ('참여율', sorted(all_summaries, key=lambda x: x['avg_engagement'], reverse=True)),
            'view_velocity': ('조회 속도', sorted(all_summaries, key=lambda x: x['avg_velocity'], reverse=True)),
            'viral_rate': ('바이럴 비율', sorted(all_summaries, key=lambda x: x['viral_rate'], reverse=True)),
            'success_rate': ('콘텐츠 성공률', sorted(all_summaries, key=lambda x: x['success_rate'], reverse=True)),
        }

        strengths, weaknesses = [], []

        for metric, (name, ranked) in rankings.items():
            key = metric_keys[metric]
            pos = next(i for i, x in enumerate(ranked) if x['channel_name'] == main_name) + 1
            my_value = main_summary.get(key, 0)
            top_value = ranked[0].get(key, 0)

            # 1위와의 격차 비율 계산
            if top_value > 0 and my_value > 0:
                gap_ratio = (top_value - my_value) / top_value * 100  # 1위 대비 몇% 뒤처지는지
            else:
                gap_ratio = 0

            gap_abs = top_value - my_value

            if pos == 1:
                # 1위면 무조건 강점
                strengths.append(f'🥇 {name} 1위 (전체 {total}개 채널 중)')
            elif gap_ratio <= 10:
                # 1위와 10% 이내 차이 → 강점 (거의 동급)
                strengths.append(f'🥈 {name} {pos}위 - 1위와 근소한 차이 ({self._format_gap(gap_abs, metric)})')
            elif gap_ratio <= 30:
                # 1위와 30% 이내 차이 → 약점이지만 개선 가능
                weaknesses.append(f'📈 {name} {pos}위 - 개선 여지 있음 (1위 대비 -{gap_ratio:.0f}%, {self._format_gap(gap_abs, metric)} 차이)')
            else:
                # 1위와 30% 초과 차이 → 심각한 약점
                weaknesses.append(f'⚠️ {name} {pos}위 - 개선 필요! (1위 대비 -{gap_ratio:.0f}%, {self._format_gap(gap_abs, metric)} 뒤처짐)')

        return {
            'strengths': strengths,
            'weaknesses': weaknesses,
            'strength_count': len(strengths),
            'weakness_count': len([w for w in weaknesses if '개선 필요' in w]),
        }

    def _format_gap(self, gap, metric):
        """격차 포맷팅"""
        if metric in ['engagement', 'avg_engagement', 'viral_rate', 'success_rate']:
            return f'{abs(gap):.1f}%p'
        elif gap >= 1000000:
            return f'{gap/1000000:.1f}M'
        elif gap >= 1000:
            return f'{gap/1000:.1f}K'
        return str(int(gap))

    def _analyze_market_position(self) -> dict:
        """시장 포지션 상세 분석"""
        main_summary = self._extract_detailed_summary(self.main)
        comp_summaries = [self._extract_detailed_summary(c) for c in self.competitors]

        if not comp_summaries:
            return {}

        avg_subs = sum(c['subscriber_count'] for c in comp_summaries) / len(comp_summaries)
        avg_views = sum(c['avg_views'] for c in comp_summaries) / len(comp_summaries)
        avg_velocity = sum(c['avg_velocity'] for c in comp_summaries) / len(comp_summaries)
        avg_engagement = sum(c['avg_engagement'] for c in comp_summaries) / len(comp_summaries)

        # 종합 점수 계산
        scores = {
            'subscriber_score': min(100, main_summary['subscriber_count'] / avg_subs * 50) if avg_subs > 0 else 50,
            'views_score': min(100, main_summary['avg_views'] / avg_views * 50) if avg_views > 0 else 50,
            'engagement_score': min(100, main_summary['avg_engagement'] / avg_engagement * 50) if avg_engagement > 0 else 50,
            'viral_score': min(100, main_summary['viral_rate'] * 5),
        }
        overall_score = sum(scores.values()) / len(scores)

        position = (
            'dominant' if overall_score >= 80 else
            'leader' if overall_score >= 60 else
            'challenger' if overall_score >= 40 else 'follower'
        )

        position_korean = {
            'dominant': '압도적 선두',
            'leader': '시장 선도자',
            'challenger': '도전자',
            'follower': '추격자'
        }

        return {
            'position': position,
            'position_korean': position_korean[position],
            'overall_score': round(overall_score, 1),
            'scores': {k: round(v, 1) for k, v in scores.items()},
            'subscriber_vs_avg': round(main_summary['subscriber_count'] / avg_subs * 100, 1) if avg_subs > 0 else 0,
            'views_vs_avg': round(main_summary['avg_views'] / avg_views * 100, 1) if avg_views > 0 else 0,
            'velocity_vs_avg': round(main_summary['avg_velocity'] / avg_velocity * 100, 1) if avg_velocity > 0 else 0,
            'engagement_vs_avg': round(main_summary['avg_engagement'] / avg_engagement * 100, 1) if avg_engagement > 0 else 0,
            'interpretation': self._interpret_position(position, overall_score),
        }

    def _interpret_position(self, position: str, score: float) -> str:
        """포지션 해석"""
        interpretations = {
            'dominant': f'경쟁사 대비 압도적인 우위에 있습니다. 현재 전략을 유지하며 시장 지배력을 강화하세요.',
            'leader': f'시장 선도 위치에 있습니다. 경쟁사의 추격에 대비하고 차별화 포인트를 강화하세요.',
            'challenger': f'경쟁력 있는 도전자 위치입니다. 특정 영역에서 차별화하여 선두권 진입을 노리세요.',
            'follower': f'시장 추격자 위치입니다. 경쟁사 대비 개선이 필요한 영역에 집중 투자하세요.',
        }
        return interpretations.get(position, '')

    def _generate_competitive_insights(self) -> list:
        """경쟁 인사이트 생성"""
        insights = []
        main_summary = self._extract_detailed_summary(self.main)
        comp_summaries = [self._extract_detailed_summary(c) for c in self.competitors]

        if not comp_summaries:
            return insights

        # 조회수 인사이트
        avg_views = sum(c['avg_views'] for c in comp_summaries) / len(comp_summaries)
        if main_summary['avg_views'] > avg_views * 1.5:
            insights.append({
                'type': 'positive',
                'title': '조회수 경쟁력 우수',
                'detail': f"경쟁사 평균 대비 {round(main_summary['avg_views']/avg_views*100-100)}% 높은 조회수를 기록하고 있습니다.",
            })
        elif main_summary['avg_views'] < avg_views * 0.7:
            insights.append({
                'type': 'negative',
                'title': '조회수 개선 필요',
                'detail': f"경쟁사 평균 대비 {round(100-main_summary['avg_views']/avg_views*100)}% 낮은 조회수입니다. 썸네일/제목 최적화가 필요합니다.",
            })

        # 바이럴 인사이트
        avg_viral = sum(c['viral_rate'] for c in comp_summaries) / len(comp_summaries)
        if main_summary['viral_rate'] > avg_viral + 10:
            insights.append({
                'type': 'positive',
                'title': '바이럴 콘텐츠 강점',
                'detail': f"바이럴 비율 {main_summary['viral_rate']}%로 경쟁사 평균({avg_viral:.1f}%) 대비 높습니다.",
            })
        elif main_summary['viral_rate'] < avg_viral - 5:
            insights.append({
                'type': 'negative',
                'title': '바이럴 콘텐츠 부족',
                'detail': f"바이럴 비율이 경쟁사 평균보다 낮습니다. 트렌드 콘텐츠 비중을 높이세요.",
            })

        # 참여율 인사이트
        avg_engagement = sum(c['avg_engagement'] for c in comp_summaries) / len(comp_summaries)
        if main_summary['avg_engagement'] > avg_engagement * 1.3:
            insights.append({
                'type': 'positive',
                'title': '높은 팬 충성도',
                'detail': f"참여율 {main_summary['avg_engagement']:.2f}%로 충성 팬층이 두텁습니다.",
            })

        # 성공률 인사이트
        avg_success = sum(c['success_rate'] for c in comp_summaries) / len(comp_summaries)
        if main_summary['success_rate'] > avg_success + 15:
            insights.append({
                'type': 'positive',
                'title': '콘텐츠 성공률 높음',
                'detail': f"히트 이상 콘텐츠 비율 {main_summary['success_rate']}%로 콘텐츠 기획력이 우수합니다.",
            })
        elif main_summary['success_rate'] < avg_success - 10:
            insights.append({
                'type': 'negative',
                'title': '콘텐츠 성공률 개선 필요',
                'detail': f"히트 이상 콘텐츠 비율이 {main_summary['success_rate']}%로 낮습니다. 콘텐츠 기획 전략 재검토가 필요합니다.",
            })

        return insights

    def _generate_competitive_recommendations(self) -> list:
        """데이터 기반 구체적 경쟁 전략 추천"""
        recommendations = []
        main = self._extract_detailed_summary(self.main)
        comp_summaries = [self._extract_detailed_summary(c) for c in self.competitors]

        if not comp_summaries:
            return recommendations

        # 경쟁사별 데이터 정리
        best_subs = max(comp_summaries, key=lambda x: x['subscriber_count'])
        best_views = max(comp_summaries, key=lambda x: x['avg_views'])
        best_engagement = max(comp_summaries, key=lambda x: x['avg_engagement'])
        best_viral = max(comp_summaries, key=lambda x: x['viral_rate'])
        best_velocity = max(comp_summaries, key=lambda x: x['avg_velocity'])

        avg_subs = sum(c['subscriber_count'] for c in comp_summaries) / len(comp_summaries)
        avg_views = sum(c['avg_views'] for c in comp_summaries) / len(comp_summaries)
        avg_engagement = sum(c['avg_engagement'] for c in comp_summaries) / len(comp_summaries)
        avg_viral = sum(c['viral_rate'] for c in comp_summaries) / len(comp_summaries)

        # 1. 구독자 성장 전략 (구체적 수치 포함)
        subs_gap = best_subs['subscriber_count'] - main['subscriber_count']
        if subs_gap > 0:
            subs_gap_str = f"{subs_gap/1000:.1f}K" if subs_gap >= 1000 else str(int(subs_gap))
            growth_rate = main.get('subscriber_count', 1) / max(best_subs.get('subscriber_count', 1), 1) * 100

            recommendations.append({
                'category': f"📈 구독자 성장 전략 (현재 {main['subscriber_count']/1000:.1f}K → 목표 {best_subs['subscriber_count']/1000:.1f}K)",
                'priority': 'critical' if growth_rate < 50 else 'high',
                'suggestions': [
                    f"1위 [{best_subs['channel_name']}]와 {subs_gap_str}명 차이 → 주간 콘텐츠 +1개 증가 필요",
                    f"[{best_subs['channel_name']}] 구독자 유입 경로 분석: 쇼츠/커뮤니티/콜라보 중 주력 채널 파악",
                    f"현재 구독자 대비 조회수 비율 {main['avg_views']/max(main['subscriber_count'],1)*100:.1f}% → 목표 15% 이상으로 개선",
                    f"구독 전환율 높은 콘텐츠 유형 파악 후 해당 포맷 비중 확대",
                ]
            })

        # 2. 조회수 개선 전략 (구체적 수치)
        views_gap = best_views['avg_views'] - main['avg_views']
        if views_gap > 0:
            views_gap_str = f"{views_gap/1000:.1f}K" if views_gap >= 1000 else str(int(views_gap))
            views_ratio = main['avg_views'] / max(best_views['avg_views'], 1) * 100

            recommendations.append({
                'category': f"👀 조회수 개선 전략 (현재 {main['avg_views']/1000:.1f}K → 목표 {best_views['avg_views']/1000:.1f}K)",
                'priority': 'critical' if views_ratio < 50 else 'high',
                'suggestions': [
                    f"1위 [{best_views['channel_name']}] 평균 조회수 {best_views['avg_views']/1000:.1f}K, 당신은 {main['avg_views']/1000:.1f}K → {views_gap_str} 격차 해소 필요",
                    f"[{best_views['channel_name']}] 최근 인기 영상 TOP 5 제목/썸네일 패턴 분석 후 적용",
                    f"CTR(클릭률) 목표: 현재 추정 {main['avg_views']/max(main['subscriber_count'],1)*100:.1f}% → {best_views['avg_views']/max(best_views['subscriber_count'],1)*100:.1f}%로 상향",
                    f"업로드 시간 최적화: [{best_views['channel_name']}] 업로드 패턴 분석 및 동일 시간대 테스트",
                ]
            })

        # 3. 참여율 개선 전략 (구체적 수치)
        eng_gap = best_engagement['avg_engagement'] - main['avg_engagement']
        if eng_gap > 0.5:  # 0.5%p 이상 차이나면
            recommendations.append({
                'category': f"💬 참여율 개선 전략 (현재 {main['avg_engagement']:.2f}% → 목표 {best_engagement['avg_engagement']:.2f}%)",
                'priority': 'high' if eng_gap > 2 else 'medium',
                'suggestions': [
                    f"1위 [{best_engagement['channel_name']}] 참여율 {best_engagement['avg_engagement']:.2f}% vs 당신 {main['avg_engagement']:.2f}% → {eng_gap:.2f}%p 개선 필요",
                    f"[{best_engagement['channel_name']}] 영상 내 CTA(Call-to-Action) 배치 방식 분석",
                    f"댓글 유도 질문 삽입: 영상 중간/끝에 시청자 의견 묻는 질문 추가",
                    f"좋아요 비율 목표: 현재 {main['avg_like_ratio']:.2f}% → 경쟁사 평균 {sum(c['avg_like_ratio'] for c in comp_summaries)/len(comp_summaries):.2f}% 달성",
                ]
            })

        # 4. 바이럴 콘텐츠 전략 (구체적 수치)
        viral_gap = best_viral['viral_rate'] - main['viral_rate']
        if viral_gap > 5:  # 5%p 이상 차이
            recommendations.append({
                'category': f"🔥 바이럴 콘텐츠 전략 (현재 {main['viral_rate']:.1f}% → 목표 {best_viral['viral_rate']:.1f}%)",
                'priority': 'high',
                'suggestions': [
                    f"1위 [{best_viral['channel_name']}] 바이럴률 {best_viral['viral_rate']:.1f}% (바이럴 {best_viral['viral_count']}개/{best_viral['total_videos']}개)",
                    f"당신의 바이럴률 {main['viral_rate']:.1f}% (바이럴 {main['viral_count']}개/{main['total_videos']}개) → {viral_gap:.1f}%p 격차",
                    f"[{best_viral['channel_name']}] 바이럴 영상 공통점 분석: 제목 키워드, 썸네일 스타일, 영상 길이",
                    f"목표: 다음 10개 영상 중 최소 {int(best_viral['viral_rate']/10)}개 바이럴 달성",
                ]
            })

        # 5. 조회 속도 개선 (구체적 수치)
        velocity_gap = best_velocity['avg_velocity'] - main['avg_velocity']
        if velocity_gap > 100:  # 일 100회 이상 차이
            recommendations.append({
                'category': f"⚡ 초기 조회 속도 전략 (현재 {main['avg_velocity']:.0f}/일 → 목표 {best_velocity['avg_velocity']:.0f}/일)",
                'priority': 'high',
                'suggestions': [
                    f"1위 [{best_velocity['channel_name']}] 일일 조회 속도 {best_velocity['avg_velocity']:.0f}회 vs 당신 {main['avg_velocity']:.0f}회",
                    f"업로드 후 24시간 내 푸시 알림 최적화 (알림 설정 유도 CTA 추가)",
                    f"SNS 동시 홍보: 업로드 즉시 트위터/인스타/커뮤니티 동시 공유",
                    f"프리미어 공개 활용: 실시간 채팅으로 초기 참여 유도",
                ]
            })

        # 6. 경쟁사별 구체적 벤치마킹 전략
        benchmark_items = []
        for comp in comp_summaries:
            advantages = []
            if comp['avg_views'] > main['avg_views'] * 1.2:
                advantages.append(f"조회수 {comp['avg_views']/1000:.1f}K")
            if comp['avg_engagement'] > main['avg_engagement'] * 1.2:
                advantages.append(f"참여율 {comp['avg_engagement']:.2f}%")
            if comp['viral_rate'] > main['viral_rate'] + 5:
                advantages.append(f"바이럴률 {comp['viral_rate']:.1f}%")

            if advantages:
                benchmark_items.append(f"[{comp['channel_name']}] 강점: {', '.join(advantages)} → 해당 채널 최근 영상 10개 분석 필수")

        if benchmark_items:
            recommendations.append({
                'category': '🎯 경쟁사별 벤치마킹 포인트',
                'priority': 'medium',
                'suggestions': benchmark_items[:4]
            })

        # 7. 내 강점 활용 전략
        my_advantages = []
        if main['avg_engagement'] >= best_engagement['avg_engagement']:
            my_advantages.append(f"참여율 1위 ({main['avg_engagement']:.2f}%) → 멤버십/후원 기능 적극 활용")
        if main['viral_rate'] >= best_viral['viral_rate']:
            my_advantages.append(f"바이럴률 1위 ({main['viral_rate']:.1f}%) → 바이럴 포맷 시리즈화하여 지속 생산")
        if main['avg_views'] >= best_views['avg_views']:
            my_advantages.append(f"조회수 1위 ({main['avg_views']/1000:.1f}K) → 스폰서십/PPL 단가 협상력 강화")
        if main['avg_velocity'] >= best_velocity['avg_velocity']:
            my_advantages.append(f"조회속도 1위 ({main['avg_velocity']:.0f}/일) → 충성 구독자층 두터움, 유료 콘텐츠 전환 고려")

        if my_advantages:
            recommendations.append({
                'category': '💪 내 강점 극대화 전략',
                'priority': 'medium',
                'suggestions': my_advantages
            })

        # 8. 종합 액션 플랜
        action_plan = []
        # 가장 큰 격차 항목 찾기
        gaps_analysis = [
            ('구독자', subs_gap if subs_gap > 0 else 0, best_subs['channel_name']),
            ('조회수', views_gap if views_gap > 0 else 0, best_views['channel_name']),
        ]
        gaps_analysis.sort(key=lambda x: x[1], reverse=True)

        if gaps_analysis[0][1] > 0:
            action_plan.append(f"최우선 과제: {gaps_analysis[0][0]} 개선 - [{gaps_analysis[0][2]}] 채널 집중 분석")

        action_plan.append(f"주간 목표: 영상 {max(2, int(main['total_videos']/4))}개 이상 업로드 유지")
        action_plan.append(f"월간 KPI: 구독자 +{int(subs_gap/12) if subs_gap > 0 else 1000}명, 평균 조회수 +{int(views_gap/12/1000) if views_gap > 0 else 1}K")

        recommendations.append({
            'category': '📋 종합 액션 플랜',
            'priority': 'critical',
            'suggestions': action_plan
        })

        return recommendations
