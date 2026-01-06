"""
Gemini API Blog Auto-Generator v3.0
Gemini 2.5 Flash API 기반 블로그 자동 생성 (bloggogogo 패턴 적용)
이미지 프롬프트 생성 + 네이버/구글 블로그 형식 지원
"""
import requests
from datetime import datetime
import json
import re
from typing import Optional, List, Dict


class BlogGenerator:
    """Gemini 2.5 Flash API 기반 블로그 생성기"""

    # Gemini API 모델 우선순위 (최신 모델부터)
    GEMINI_MODELS = [
        'gemini-2.5-flash',      # 최신 (사용자 요청)
        'gemini-2.0-flash',      # 백업 1
        'gemini-2.5-flash-lite', # 백업 2
        'gemini-2.5-pro',        # 백업 3
    ]

    # 컬러 테마 (bidbuycontents 스타일 - 10가지)
    THEMES = {
        'teal-mint': {
            'name': '틸-민트',
            'primary': '#00897b',
            'secondary': '#e0f2f1',
            'accent': '#b2dfdb',
            'tableBg': '#e0f2f1',
        },
        'blue-sky': {
            'name': '블루-스카이',
            'primary': '#1976d2',
            'secondary': '#e3f2fd',
            'accent': '#bbdefb',
            'tableBg': '#e3f2fd',
        },
        'orange-warm': {
            'name': '오렌지-웜',
            'primary': '#f57c00',
            'secondary': '#fff3e0',
            'accent': '#ffe0b2',
            'tableBg': '#fff3e0',
        },
        'purple-lavender': {
            'name': '퍼플-라벤더',
            'primary': '#7b1fa2',
            'secondary': '#f3e5f5',
            'accent': '#e1bee7',
            'tableBg': '#f3e5f5',
        },
        'green-forest': {
            'name': '그린-포레스트',
            'primary': '#388e3c',
            'secondary': '#e8f5e9',
            'accent': '#c8e6c9',
            'tableBg': '#e8f5e9',
        },
        'red-coral': {
            'name': '레드-코랄',
            'primary': '#d32f2f',
            'secondary': '#ffebee',
            'accent': '#ffcdd2',
            'tableBg': '#ffebee',
        },
        'indigo-night': {
            'name': '인디고-나이트',
            'primary': '#3949ab',
            'secondary': '#e8eaf6',
            'accent': '#c5cae9',
            'tableBg': '#e8eaf6',
        },
        'pink-rose': {
            'name': '핑크-로즈',
            'primary': '#e91e63',
            'secondary': '#fce4ec',
            'accent': '#f8bbd9',
            'tableBg': '#fce4ec',
        },
        'brown-earth': {
            'name': '브라운-어스',
            'primary': '#795548',
            'secondary': '#efebe9',
            'accent': '#d7ccc8',
            'tableBg': '#efebe9',
        },
        'cyan-ocean': {
            'name': '시안-오션',
            'primary': '#0097a7',
            'secondary': '#e0f7fa',
            'accent': '#b2ebf2',
            'tableBg': '#e0f7fa',
        },
        # 기존 호환 테마
        'blue-gray': {
            'name': '블루-그레이',
            'primary': '#1a73e8',
            'secondary': '#f5f5f5',
            'accent': '#e8f4fd',
            'tableBg': '#f5f5f5',
        },
        'green-orange': {
            'name': '그린-오렌지',
            'primary': '#2e7d32',
            'secondary': '#f1f8e9',
            'accent': '#fff3e0',
            'tableBg': '#f1f8e9',
        },
        'purple-yellow': {
            'name': '퍼플-옐로우',
            'primary': '#7b1fa2',
            'secondary': '#f3e5f5',
            'accent': '#fffde7',
            'tableBg': '#f3e5f5',
        },
        'teal-gray': {
            'name': '틸-라이트그레이',
            'primary': '#00796b',
            'secondary': '#e0f2f1',
            'accent': '#e0f7fa',
            'tableBg': '#e0f2f1',
        },
        'terracotta': {
            'name': '테라코타-라이트그레이',
            'primary': '#bf360c',
            'secondary': '#fbe9e7',
            'accent': '#ffe0b2',
            'tableBg': '#fbe9e7',
        },
    }

    def __init__(self, api_key: str):
        """Gemini API 초기화"""
        self.api_key = api_key
        self.base_url = "https://generativelanguage.googleapis.com/v1beta/models"
        self.current_model = None

    def _call_gemini_api(self, prompt: str, max_tokens: int = 16384, temperature: float = 0.7) -> str:
        """Gemini API 호출 (여러 모델 시도 패턴)"""
        last_error = None

        for model in self.GEMINI_MODELS:
            try:
                print(f"[INFO] {model} 모델로 시도 중...")
                url = f"{self.base_url}/{model}:generateContent?key={self.api_key}"

                payload = {
                    "contents": [{
                        "parts": [{
                            "text": prompt
                        }]
                    }],
                    "generationConfig": {
                        "temperature": temperature,
                        "maxOutputTokens": max_tokens,
                    }
                }

                response = requests.post(url, json=payload, timeout=60)
                response.raise_for_status()

                data = response.json()

                # 응답 검증
                if not data.get('candidates') or not data['candidates'][0]:
                    print(f"[WARN] {model} 응답 없음")
                    continue

                candidate = data['candidates'][0]
                if not candidate.get('content') or not candidate['content'].get('parts'):
                    print(f"[WARN] {model} content 없음")
                    continue

                self.current_model = model
                print(f"[INFO] {model} 모델 사용 성공!")
                return candidate['content']['parts'][0]['text']

            except requests.exceptions.HTTPError as e:
                error_msg = str(e)
                if e.response is not None:
                    try:
                        error_data = e.response.json()
                        error_msg = error_data.get('error', {}).get('message', str(e))
                    except:
                        pass
                print(f"[WARN] {model} 모델 실패: {error_msg}")
                last_error = e
                continue

            except Exception as e:
                print(f"[WARN] {model} 모델 실패: {str(e)}")
                last_error = e
                continue

        raise Exception(f"모든 Gemini 모델 호출 실패: {last_error}")

    def generate_blog_from_video(self, video_data: dict, analysis: dict = None,
                                 platform: str = 'naver', theme: str = 'blue-gray') -> dict:
        """영상 데이터 기반 블로그 포스트 생성 (이미지 프롬프트 포함)"""

        theme_info = self.THEMES.get(theme, self.THEMES['blue-sky'])
        platform_guide = self._get_platform_guide(platform)

        # 프롬프트 구성 (bidbuycontents 스타일)
        prompt = self._build_video_blog_prompt_v3(video_data, analysis, platform_guide, theme_info)

        try:
            response_text = self._call_gemini_api(prompt)

            # JSON 파싱
            result = self._parse_json_response(response_text)

            # HTML 콘텐츠 정리
            html_content = result.get('content', '')
            html_content = self._clean_html_content(html_content, theme_info)

            return {
                'success': True,
                'title': result.get('title', video_data.get('title', '제목 없음')),
                'content': html_content,
                'meta_description': result.get('meta_description', ''),
                'keywords': result.get('keywords', []),
                'hashtags': result.get('hashtags', []),
                'thumbnail_prompt': result.get('thumbnail_prompt', ''),
                'image_prompts': result.get('image_prompts', []),
                'platform': platform,
                'theme': theme,
                'video_id': video_data.get('video_id'),
                'model_used': self.current_model,
                'generated_at': datetime.now().isoformat(),
            }

        except Exception as e:
            return {
                'success': False,
                'error': str(e),
            }

    def generate_blog_from_analysis(self, channel_analysis: dict, topic: str = None,
                                    platform: str = 'naver', theme: str = 'blue-gray') -> dict:
        """채널 분석 결과 기반 블로그 포스트 생성"""

        theme_info = self.THEMES.get(theme, self.THEMES['blue-sky'])
        platform_guide = self._get_platform_guide(platform)

        prompt = self._build_analysis_blog_prompt_v3(channel_analysis, topic, platform_guide, theme_info)

        try:
            response_text = self._call_gemini_api(prompt)
            result = self._parse_json_response(response_text)

            html_content = result.get('content', '')
            html_content = self._clean_html_content(html_content, theme_info)

            return {
                'success': True,
                'title': result.get('title', topic or '채널 분석 리포트'),
                'content': html_content,
                'meta_description': result.get('meta_description', ''),
                'keywords': result.get('keywords', []),
                'hashtags': result.get('hashtags', []),
                'thumbnail_prompt': result.get('thumbnail_prompt', ''),
                'image_prompts': result.get('image_prompts', []),
                'platform': platform,
                'theme': theme,
                'model_used': self.current_model,
                'generated_at': datetime.now().isoformat(),
            }

        except Exception as e:
            return {
                'success': False,
                'error': str(e),
            }

    def generate_image_prompts(self, topic: str, count: int = 3) -> dict:
        """이미지 프롬프트 생성 (bidbuycontents 스타일)"""

        prompt = f"""다음 주제에 맞는 이미지 생성 프롬프트를 {count}개 만들어주세요:

주제: {topic}

요구사항:
1. 주제와 관련된 전문적이고 신뢰감 있는 이미지
2. 사진 스타일의 현실적인 이미지 (일러스트 X)
3. 글의 맥락에 맞는 고품질 이미지
4. 텍스트나 로고가 없는 순수한 이미지
5. 각 프롬프트는 100자 이내의 영어로 작성
6. {count}개의 서로 다른 각도/구도/스타일로 다양하게 생성

출력 형식 (JSON만):
{{
  "prompts": [
    {{"prompt": "영어 프롬프트 1", "suggestion": "활용 팁 1"}},
    {{"prompt": "영어 프롬프트 2", "suggestion": "활용 팁 2"}}
  ]
}}

JSON만 출력. 다른 텍스트 금지."""

        try:
            response_text = self._call_gemini_api(prompt, max_tokens=1000)
            result = self._parse_json_response(response_text)

            return {
                'success': True,
                'prompts': result.get('prompts', []),
                'model_used': self.current_model,
            }

        except Exception as e:
            return {
                'success': False,
                'error': str(e),
                'prompts': [],
            }

    def _build_video_blog_prompt_v3(self, video_data: dict, analysis: dict,
                                    platform_guide: dict, theme_info: dict) -> str:
        """영상 기반 블로그 프롬프트 v3 (bidbuycontents 스타일)"""

        video_title = video_data.get('title', '')
        video_desc = video_data.get('description', '')[:500]
        view_count = video_data.get('view_count', 0)
        like_count = video_data.get('like_count', 0)
        tags = ', '.join(video_data.get('tags', [])[:10])

        # 분석 정보
        analysis_text = ""
        if analysis:
            classification = analysis.get('classification', '')
            engagement = analysis.get('engagement_rate', 0)
            score = analysis.get('algorithm_score', 0)
            analysis_text = f"""
## 분석 인사이트
- 성과 분류: {classification}
- 참여율: {engagement:.2f}%
- 알고리즘 점수: {score:.1f}점
"""

        return f"""YouTube 영상 기반 블로그 글 작성

## 영상 정보
제목: {video_title}
설명: {video_desc}
조회수: {view_count:,}회
좋아요: {like_count:,}개
태그: {tags}
{analysis_text}

## 테마: {theme_info['name']}
primary: {theme_info['primary']}
secondary: {theme_info['secondary']}
accent: {theme_info['accent']}
tableBg: {theme_info['tableBg']}

## 필수 요구사항
- 3,000-3,500자 (한글, 공백 포함)
- ~이에요, ~해요 체 (친근하고 읽기 쉽게)
- 유튜버/채널명 절대 언급 금지! 마치 내가 직접 경험한 것처럼 1인칭으로 작성
- 문단 사이 충분한 여백 (각 p 태그에 margin-bottom: 20px 적용)

## 플랫폼: {platform_guide['name']}
{platform_guide['guidelines']}

## HTML 구조 (깔끔하고 미니멀하게)
<div style="font-family: 'Noto Sans KR', sans-serif; line-height: 1.9; max-width: 800px; margin: 0 auto; font-size: 17px; color: #333;">
  <div style="background: linear-gradient(135deg, {theme_info['secondary']}, #fff); padding: 20px; border-radius: 12px; margin-bottom: 30px;">
    <strong>[호기심 유발 질문]</strong><br>
    <span style="color: #666;">[질문에 대한 간단한 답변 미리보기]</span>
  </div>

  <p style="margin-bottom: 20px; line-height: 1.9;">[도입 - 왜 이 주제에 관심을 갖게 됐는지]</p>

  {{{{IMAGE_1}}}}

  <h2 style="font-size: 22px; color: {theme_info['primary']}; margin: 40px 0 20px; padding-bottom: 10px; border-bottom: 2px solid {theme_info['accent']};">[섹션1 제목]</h2>
  <p style="margin-bottom: 20px; line-height: 1.9;">[본문 - 구체적인 내용]</p>

  {{{{IMAGE_2}}}}

  <h2 style="font-size: 22px; color: {theme_info['primary']}; margin: 40px 0 20px; padding-bottom: 10px; border-bottom: 2px solid {theme_info['accent']};">[섹션2 제목]</h2>
  <p style="margin-bottom: 20px; line-height: 1.9;">[본문]</p>

  <div style="background-color: {theme_info['secondary']}; padding: 20px; margin: 30px 0; border-radius: 8px;">
    <strong style="color: {theme_info['primary']};">Tip</strong>
    <p style="margin: 10px 0 0;">[실용적인 팁]</p>
  </div>

  <table style="width: 100%; border-collapse: collapse; margin: 30px 0; border-radius: 8px; overflow: hidden;">
    <thead>
      <tr style="background-color: {theme_info['primary']};">
        <th style="padding: 14px 16px; text-align: left; font-weight: 600; color: white;">[항목]</th>
        <th style="padding: 14px 16px; text-align: left; font-weight: 600; color: white;">[내용]</th>
      </tr>
    </thead>
    <tbody>
      <tr style="background-color: {theme_info['tableBg']};">
        <td style="padding: 14px 16px; border-bottom: 1px solid #eee; color: #333;">[데이터]</td>
        <td style="padding: 14px 16px; border-bottom: 1px solid #eee; color: #333;">[데이터]</td>
      </tr>
    </tbody>
  </table>

  {{{{IMAGE_3}}}}

  <h2 style="font-size: 22px; color: {theme_info['primary']}; margin: 40px 0 20px; padding-bottom: 10px; border-bottom: 2px solid {theme_info['accent']};">자주 묻는 질문</h2>
  <h3 style="font-size: 17px; margin: 25px 0 10px; color: #333; font-weight: 600;">Q. [질문1]?</h3>
  <p style="margin-bottom: 20px; line-height: 1.9; color: #555;">[답변1]</p>
  <h3 style="font-size: 17px; margin: 25px 0 10px; color: #333; font-weight: 600;">Q. [질문2]?</h3>
  <p style="margin-bottom: 20px; line-height: 1.9; color: #555;">[답변2]</p>

  <div style="background: {theme_info['secondary']}; padding: 24px; border-radius: 12px; margin-top: 40px;">
    <strong style="color: {theme_info['primary']};">마무리</strong>
    <p style="margin: 12px 0 0; line-height: 1.9;">[전체 요약 및 추천 멘트]</p>
  </div>
</div>

## 이미지 프롬프트 규칙
- 영상 주제와 관련된 **실제 상황**을 구체적으로 묘사
- 영어로 작성, photorealistic 스타일
- 3개의 다른 구도/장면으로 생성

## JSON 출력 (필수!)
{{
  "title": "SEO 최적화 제목 60자 이내",
  "meta_description": "메타 설명 130-150자",
  "content": "위 HTML 구조의 완전한 본문",
  "keywords": ["키워드1", "키워드2", "키워드3", "키워드4", "키워드5", "키워드6", "키워드7", "키워드8"],
  "hashtags": ["해시태그1", "해시태그2", "해시태그3", "해시태그4", "해시태그5"],
  "thumbnail_prompt": "메인 주제 영어 프롬프트, photorealistic, 16:9",
  "image_prompts": ["영어 프롬프트1", "영어 프롬프트2", "영어 프롬프트3"]
}}

JSON만 출력. 다른 텍스트 금지."""

    def _build_analysis_blog_prompt_v3(self, analysis: dict, topic: str,
                                       platform_guide: dict, theme_info: dict) -> str:
        """분석 기반 블로그 프롬프트 v3"""

        channel_summary = analysis.get('channel_summary', {})
        success_analysis = analysis.get('success_analysis', {})
        algorithm_health = analysis.get('algorithm_health', {})
        recommendations = analysis.get('recommendations', [])

        return f"""YouTube 채널 분석 기반 블로그 글 작성

## 채널 분석 요약
- 채널명: {channel_summary.get('channel_name', '')}
- 구독자: {channel_summary.get('subscriber_count', 0):,}명
- 분석 영상: {channel_summary.get('total_videos_analyzed', 0)}개
- 평균 조회수: {channel_summary.get('avg_views_per_video', 0):,}회
- 평균 참여율: {channel_summary.get('avg_engagement_rate', 0):.2f}%

## 알고리즘 건강도
{json.dumps(algorithm_health, ensure_ascii=False, indent=2)}

## 성공 영상 패턴
{json.dumps(success_analysis.get('success_patterns', [])[:5], ensure_ascii=False, indent=2)}

## 추천사항
{json.dumps([r.get('suggestions', [])[:3] for r in recommendations[:3]], ensure_ascii=False, indent=2)}

## 블로그 주제
{topic or '유튜브 채널 성장 전략과 인사이트'}

## 테마: {theme_info['name']}
primary: {theme_info['primary']}
secondary: {theme_info['secondary']}

## 플랫폼: {platform_guide['name']}
{platform_guide['guidelines']}

## 필수 요구사항
- 2,500-3,000자 (한글 기준)
- 친근하지만 전문적인 어조
- 데이터 기반: 분석 수치를 자연스럽게 인용
- 실용적 조언: 독자가 바로 적용할 수 있는 팁 포함

## HTML 구조
<div style="font-family: 'Noto Sans KR', sans-serif; line-height: 1.9; max-width: 800px; margin: 0 auto; font-size: 17px; color: #333;">
  [본문 콘텐츠 - 위의 분석 데이터를 활용하여 작성]
</div>

## JSON 출력 (필수!)
{{
  "title": "SEO 최적화 제목 60자 이내",
  "meta_description": "메타 설명 130-150자",
  "content": "HTML 본문",
  "keywords": ["키워드1", "키워드2", "키워드3", "키워드4", "키워드5"],
  "hashtags": ["해시태그1", "해시태그2", "해시태그3", "해시태그4", "해시태그5"],
  "thumbnail_prompt": "채널 분석 관련 영어 프롬프트, professional, 16:9",
  "image_prompts": ["영어 프롬프트1", "영어 프롬프트2", "영어 프롬프트3"]
}}

JSON만 출력. 다른 텍스트 금지."""

    def _get_platform_guide(self, platform: str) -> dict:
        """플랫폼별 가이드라인"""
        guides = {
            'naver': {
                'name': '네이버 블로그',
                'guidelines': '''
- 검색 최적화: 제목에 핵심 키워드 포함
- 시각 자료: 이미지, 표, 박스 적극 활용
- 문단 구조: 짧은 문단, 여백 충분히
- 모바일 최적화: 가독성 중시
'''
            },
            'google': {
                'name': '구글 블로거/워드프레스',
                'guidelines': '''
- SEO: 메타 설명, 구조화된 데이터 중요
- 본문 구조: H2, H3 계층적 사용
- 내부 링크: 관련 콘텐츠 연결
- FAQ 스키마 포함 권장
'''
            },
            'tistory': {
                'name': '티스토리',
                'guidelines': '''
- data-ke-size 속성 활용
- 반응형 스타일 적용
- 목차 자동 생성 고려
- 공유 버튼 영역 확보
'''
            }
        }
        return guides.get(platform, guides['naver'])

    def _parse_json_response(self, text: str) -> dict:
        """JSON 응답 파싱 (강화된 에러 처리)"""
        # 코드블록 제거
        cleaned = text.strip()
        cleaned = re.sub(r'```json\s*', '', cleaned)
        cleaned = re.sub(r'```\s*', '', cleaned)

        # JSON 객체만 추출
        json_match = re.search(r'\{[\s\S]*\}', cleaned)
        if json_match:
            cleaned = json_match.group(0)

        # 잘못된 제어 문자 제거
        cleaned = re.sub(r'[\x00-\x1F\x7F]', '', cleaned)

        try:
            return json.loads(cleaned)
        except json.JSONDecodeError as e:
            print(f"[ERROR] JSON 파싱 실패: {e}")
            print(f"[DEBUG] 파싱 시도 텍스트 (처음 500자): {cleaned[:500]}")

            # 기본 구조 반환
            return {
                'title': '',
                'content': cleaned,
                'meta_description': '',
                'keywords': [],
                'hashtags': [],
                'thumbnail_prompt': '',
                'image_prompts': [],
            }

    def _clean_html_content(self, html: str, theme_info: dict) -> str:
        """HTML 콘텐츠 정리"""
        # 이중 이스케이프 수정
        html = html.replace('\\\\n', '\n')
        html = html.replace('\\n', '\n')
        html = html.replace('\\"', '"')

        # 래퍼 div가 없으면 추가
        if not html.strip().startswith('<div'):
            html = f'''<div style="font-family: 'Noto Sans KR', sans-serif; line-height: 1.9; max-width: 800px; margin: 0 auto; font-size: 17px; color: #333;">
{html}
</div>'''

        return html

    def generate_content_calendar(self, analysis: dict, weeks: int = 4) -> list:
        """콘텐츠 캘린더 생성"""
        success_patterns = analysis.get('success_analysis', {}).get('success_patterns', [])
        top_keywords = analysis.get('content_patterns', {}).get('top_keywords', [])

        prompt = f"""
다음 YouTube 채널 분석 데이터를 바탕으로 {weeks}주간의 블로그 콘텐츠 캘린더를 생성해주세요.

## 성공 패턴
{json.dumps(success_patterns[:5], ensure_ascii=False)}

## 인기 키워드
{json.dumps(top_keywords[:10], ensure_ascii=False)}

각 주별로 2-3개의 블로그 주제를 제안해주세요.

JSON 형식으로 출력:
[
  {{"week": 1, "topics": [{{"title": "제목", "keywords": ["키워드"], "type": "유형"}}]}}
]

JSON만 출력."""

        try:
            response_text = self._call_gemini_api(prompt, max_tokens=2000)
            json_match = re.search(r'\[[\s\S]*\]', response_text)
            if json_match:
                return json.loads(json_match.group())
        except Exception as e:
            print(f"[ERROR] 캘린더 생성 실패: {e}")

        return []


class BlogTemplates:
    """미리 정의된 블로그 템플릿"""

    @staticmethod
    def get_video_review_template(theme: dict) -> str:
        """영상 리뷰 템플릿"""
        return f'''
<div style="font-family: 'Noto Sans KR', sans-serif; line-height: 1.9; max-width: 800px; margin: 0 auto; font-size: 17px; color: #333;">

    <div style="background-color: {theme['secondary']}; padding: 20px; border-radius: 12px; font-style: italic; margin-bottom: 25px;">
        <strong>{{{{meta_title}}}}</strong> {{{{meta_description}}}}
    </div>

    <p style="margin-bottom: 20px;">{{{{intro}}}}</p>

    <h2 style="font-size: 22px; color: {theme['primary']}; margin: 40px 0 20px; padding-bottom: 10px; border-bottom: 2px solid {theme['accent']};">
        <strong>{{{{section1_title}}}}</strong>
    </h2>
    <p style="margin-bottom: 20px;">{{{{section1_content}}}}</p>

    <div style="background-color: {theme['secondary']}; border-left: 4px solid {theme['primary']}; padding: 15px; margin: 20px 0; border-radius: 0 8px 8px 0;">
        <strong>Tip</strong><br>
        {{{{tip_content}}}}
    </div>

    <h2 style="font-size: 22px; color: {theme['primary']}; margin: 40px 0 20px; padding-bottom: 10px; border-bottom: 2px solid {theme['accent']};">
        <strong>핵심 요약</strong>
    </h2>
    <p style="margin-bottom: 20px;">{{{{summary}}}}</p>

    <h2 style="font-size: 22px; color: {theme['primary']}; margin: 40px 0 20px; padding-bottom: 10px; border-bottom: 2px solid {theme['accent']};">
        <strong>자주 묻는 질문</strong>
    </h2>

    <div style="margin: 30px 0;">
        {{{{faq_content}}}}
    </div>

    <p style="margin-bottom: 20px;">{{{{outro}}}}</p>

</div>
'''

    @staticmethod
    def get_analysis_report_template(theme: dict) -> str:
        """분석 보고서 템플릿"""
        return f'''
<div style="font-family: 'Noto Sans KR', sans-serif; line-height: 1.9; max-width: 800px; margin: 0 auto; color: #333;">

    <div style="background: linear-gradient(135deg, {theme['primary']}, #4285f4); color: white; padding: 30px; border-radius: 12px; margin-bottom: 25px;">
        <h1 style="margin: 0 0 10px; font-size: 28px;">{{{{report_title}}}}</h1>
        <p style="margin: 0; opacity: 0.9;">{{{{report_subtitle}}}}</p>
    </div>

    <div style="background-color: {theme['secondary']}; padding: 20px; border-radius: 8px; margin-bottom: 25px;">
        {{{{summary_cards}}}}
    </div>

    {{{{main_content}}}}

    <div style="background-color: {theme['secondary']}; padding: 20px; border-radius: 8px; margin: 25px 0;">
        <h3 style="color: {theme['primary']}; margin: 0 0 15px;">핵심 인사이트</h3>
        {{{{key_insights}}}}
    </div>

    {{{{recommendations}}}}

    <div style="border-top: 1px dashed {theme['accent']}; margin-top: 30px; padding-top: 20px; text-align: center; color: #777;">
        <p>{{{{footer}}}}</p>
    </div>

</div>
'''
