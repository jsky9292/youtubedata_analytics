# YouTube Analytics Dashboard

유튜브 채널 분석 및 경쟁사 비교 도구

## 설치 방법

### 1. 필수 프로그램 설치

**Python 3.8 이상 필요**
- https://www.python.org/downloads/

**wkhtmltopdf (PDF 생성용)**
```bash
# Windows (Chocolatey)
choco install wkhtmltopdf

# 또는 직접 다운로드
# https://wkhtmltopdf.org/downloads.html
```

### 2. 프로젝트 클론

```bash
git clone https://github.com/본인아이디/youtubedata_analytics.git
cd youtubedata_analytics
```

### 3. 패키지 설치

```bash
pip install -r requirements.txt
```

### 4. 서버 실행

```bash
cd backend
python main.py
```

### 5. 브라우저에서 접속

```
http://localhost:8888
```

## 사용 방법

1. **API 설정 탭**: YouTube Data API 키 입력
   - [Google Cloud Console](https://console.cloud.google.com/apis/credentials)에서 발급

2. **채널 관리 탭**: 분석할 채널 추가
   - 채널 URL 또는 @핸들 입력

3. **채널 분석 탭**: 채널 선택 후 분석 실행
   - PDF, PPT, HTML, JSON 다운로드 가능

4. **경쟁사 분석 탭**: 내 채널과 경쟁 채널 비교
   - PDF, HTML, JSON 다운로드 가능

5. **블로그 생성 탭**: 분석 데이터 기반 블로그 자동 생성
   - Gemini API 키 필요

## API 키 발급

### YouTube Data API
1. [Google Cloud Console](https://console.cloud.google.com/) 접속
2. 새 프로젝트 생성
3. YouTube Data API v3 활성화
4. 사용자 인증 정보 > API 키 만들기

### Gemini API (블로그 생성용, 선택)
1. [Google AI Studio](https://makersuite.google.com/app/apikey) 접속
2. API 키 발급

## 기술 스택

- **Backend**: Python, FastAPI
- **Frontend**: HTML, CSS, JavaScript, Chart.js
- **Database**: SQLite
- **PDF 생성**: pdfkit (wkhtmltopdf)
- **PPT 생성**: python-pptx

## 주요 기능

- 채널 성과 분석 (조회수, 참여율, 알고리즘 점수)
- 영상별 성과 분류 (바이럴, 히트, 평균, 저조)
- 성공/실패 패턴 분석
- 경쟁사 비교 분석
- 데이터 기반 전략 추천
- 보고서 다운로드 (PDF, PPT, HTML, JSON)
- 블로그 자동 생성
