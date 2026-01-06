"""
YouTube Analytics API Server
FastAPI 기반 유튜브 분석 백엔드 서버
"""
from fastapi import FastAPI, HTTPException, Query, Response
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse, JSONResponse, FileResponse
from datetime import datetime
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
from typing import Optional, List
import json
import sys
import os
from pathlib import Path

# 모듈 경로 추가
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from database import (
    init_database, save_channel, get_channel, get_all_channels,
    save_video, get_videos_by_channel, save_analysis_report,
    get_latest_report, save_blog_post, get_blog_posts
)
from youtube_api import YouTubeAPIService
from analyzer import ChannelAnalyzer, CompetitorAnalyzer
from report_generator import ReportGenerator, CompetitorReportGenerator
from blog_generator import BlogGenerator

# FastAPI 앱 초기화
app = FastAPI(
    title="YouTube Analytics API",
    description="유튜브 채널 분석 및 블로그 자동생성 API",
    version="1.0.0"
)

# CORS 설정
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 데이터베이스 초기화
init_database()


# === Pydantic 모델 ===

class ChannelRequest(BaseModel):
    channel_url: str
    youtube_api_key: str
    video_count: Optional[int] = 50


class CompetitorRequest(BaseModel):
    main_channel_url: str
    competitor_urls: List[str]
    youtube_api_key: str
    video_count: Optional[int] = 30


class BlogRequest(BaseModel):
    channel_id: str
    video_id: Optional[str] = None
    gemini_api_key: str
    platform: Optional[str] = "naver"
    theme: Optional[str] = "blue-gray"
    topic: Optional[str] = None


class APIKeyStore:
    """API 키 임시 저장 (세션용)"""
    youtube_key: str = None
    gemini_key: str = None


# === 채널 관련 엔드포인트 ===

@app.post("/api/channels/add")
async def add_channel(request: ChannelRequest):
    """채널 추가 및 기본 정보 수집"""
    try:
        print(f"[API] 채널 추가 요청: {request.channel_url}")
        youtube = YouTubeAPIService(request.youtube_api_key)

        # 채널 ID 추출
        channel_id = youtube.extract_channel_id(request.channel_url)
        print(f"[API] 추출된 채널 ID: {channel_id}")

        # 채널 정보 조회
        channel_info = youtube.get_channel_info(channel_id)
        print(f"[API] 채널 정보: {channel_info.get('channel_name')}")

        # DB 저장
        save_channel(channel_info)

        return {
            "success": True,
            "channel": channel_info,
            "message": f"채널 '{channel_info['channel_name']}'이(가) 추가되었습니다."
        }

    except Exception as e:
        import traceback
        print(f"[ERROR] 채널 추가 실패: {str(e)}")
        print(traceback.format_exc())
        raise HTTPException(status_code=400, detail=str(e))


@app.get("/api/channels")
async def list_channels():
    """저장된 채널 목록 조회"""
    channels = get_all_channels()
    return {"channels": channels, "count": len(channels)}


@app.get("/api/channels/{channel_id}")
async def get_channel_detail(channel_id: str):
    """채널 상세 정보 조회"""
    channel = get_channel(channel_id)
    if not channel:
        raise HTTPException(status_code=404, detail="채널을 찾을 수 없습니다.")
    return {"channel": channel}


# === 분석 관련 엔드포인트 ===

@app.post("/api/analyze")
async def analyze_channel(request: ChannelRequest):
    """채널 심층 분석 수행"""
    try:
        youtube = YouTubeAPIService(request.youtube_api_key)

        # 채널 ID 추출 및 정보 조회
        channel_id = youtube.extract_channel_id(request.channel_url)
        channel_info = youtube.get_channel_info(channel_id)

        # 영상 목록 조회
        videos = youtube.get_channel_videos(channel_id, request.video_count)

        if not videos:
            raise HTTPException(status_code=400, detail="분석할 영상이 없습니다.")

        # 영상 정보 저장
        for video in videos:
            save_video(video)

        # 채널 정보 저장/업데이트
        save_channel(channel_info)

        # 분석 수행
        analyzer = ChannelAnalyzer(channel_info, videos)
        analysis_result = analyzer.analyze()

        # 분석 결과 저장
        save_analysis_report(channel_id, 'full_analysis', analysis_result)

        # 보고서 생성
        report_gen = ReportGenerator(analysis_result, channel_info)
        html_report = report_gen.generate_html_report()
        text_summary = report_gen.generate_summary_text()

        return {
            "success": True,
            "channel_id": channel_id,
            "channel_name": channel_info.get('channel_name'),
            "videos_analyzed": len(videos),
            "analysis": analysis_result,
            "html_report": html_report,
            "text_summary": text_summary,
        }

    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@app.post("/api/analyze/competitors")
async def analyze_competitors(request: CompetitorRequest):
    """경쟁사 비교 분석"""
    try:
        youtube = YouTubeAPIService(request.youtube_api_key)

        # 메인 채널 분석
        main_channel_id = youtube.extract_channel_id(request.main_channel_url)
        main_info = youtube.get_channel_info(main_channel_id)
        main_videos = youtube.get_channel_videos(main_channel_id, request.video_count)

        main_analyzer = ChannelAnalyzer(main_info, main_videos)
        main_analysis = main_analyzer.analyze()

        # 경쟁사 채널 분석
        competitor_analyses = []
        for comp_url in request.competitor_urls[:5]:  # 최대 5개
            try:
                comp_id = youtube.extract_channel_id(comp_url)
                comp_info = youtube.get_channel_info(comp_id)
                comp_videos = youtube.get_channel_videos(comp_id, request.video_count)

                comp_analyzer = ChannelAnalyzer(comp_info, comp_videos)
                comp_analysis = comp_analyzer.analyze()
                competitor_analyses.append(comp_analysis)

                # 저장
                save_channel(comp_info)
                for video in comp_videos:
                    save_video(video)

            except Exception as e:
                print(f"경쟁사 분석 실패: {comp_url} - {e}")
                continue

        if not competitor_analyses:
            raise HTTPException(status_code=400, detail="경쟁사 분석에 실패했습니다.")

        # 경쟁사 비교 분석
        comp_analyzer = CompetitorAnalyzer(main_analysis, competitor_analyses)
        comparison = comp_analyzer.analyze()

        # 분석 결과 저장 (나중에 다운로드용)
        save_analysis_report(main_channel_id, 'competitor_analysis', comparison)

        # 보고서 생성
        report_gen = CompetitorReportGenerator(comparison)
        html_report = report_gen.generate_html_report()

        return {
            "success": True,
            "main_channel": main_info.get('channel_name'),
            "main_channel_id": main_channel_id,
            "competitors_analyzed": len(competitor_analyses),
            "comparison": comparison,
            "html_report": html_report,
        }

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@app.get("/api/analyze/competitors/{channel_id}/report")
async def get_competitor_report(channel_id: str, format: str = Query("html", enum=["html", "json", "pdf"])):
    """경쟁사 비교 분석 보고서 다운로드 (HTML, JSON, PDF)"""
    report = get_latest_report(channel_id, 'competitor_analysis')
    if not report:
        raise HTTPException(status_code=404, detail="경쟁사 분석 보고서를 찾을 수 없습니다.")

    comparison_data = report['report_data']
    report_gen = CompetitorReportGenerator(comparison_data)
    main_channel_name = comparison_data.get('main_channel', {}).get('channel_name', 'competitor')

    if format == "html":
        return HTMLResponse(content=report_gen.generate_html_report())
    elif format == "pdf":
        try:
            from urllib.parse import quote
            pdf_bytes = report_gen.generate_pdf_report()
            filename = f"competitor_report_{main_channel_name}_{datetime.now().strftime('%Y%m%d')}.pdf"
            encoded_filename = quote(filename, safe='')
            return Response(
                content=pdf_bytes,
                media_type="application/pdf",
                headers={"Content-Disposition": f"attachment; filename*=UTF-8''{encoded_filename}"}
            )
        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))
    else:  # json
        return JSONResponse(content=comparison_data)


@app.get("/api/analyze/{channel_id}/report")
async def get_analysis_report(channel_id: str, format: str = Query("html", enum=["html", "json", "text", "pdf", "pptx"])):
    """저장된 분석 보고서 조회 (HTML, JSON, Text, PDF, PPTX)"""
    report = get_latest_report(channel_id, 'full_analysis')
    if not report:
        raise HTTPException(status_code=404, detail="분석 보고서를 찾을 수 없습니다.")

    channel = get_channel(channel_id)

    if format == "html":
        report_gen = ReportGenerator(report['report_data'], channel)
        return HTMLResponse(content=report_gen.generate_html_report())
    elif format == "text":
        report_gen = ReportGenerator(report['report_data'], channel)
        return {"text": report_gen.generate_summary_text()}
    elif format == "pdf":
        report_gen = ReportGenerator(report['report_data'], channel)
        try:
            from urllib.parse import quote
            pdf_bytes = report_gen.generate_pdf_report()
            channel_name = channel.get('channel_name', 'channel') if channel else 'channel'
            # URL 인코딩하여 한글 파일명 처리
            filename = f"youtube_report_{channel_name}_{datetime.now().strftime('%Y%m%d')}.pdf"
            encoded_filename = quote(filename, safe='')
            return Response(
                content=pdf_bytes,
                media_type="application/pdf",
                headers={"Content-Disposition": f"attachment; filename*=UTF-8''{encoded_filename}"}
            )
        except ImportError as e:
            raise HTTPException(status_code=500, detail=str(e))
    elif format == "pptx":
        report_gen = ReportGenerator(report['report_data'], channel)
        try:
            from urllib.parse import quote
            pptx_bytes = report_gen.generate_pptx_report()
            channel_name = channel.get('channel_name', 'channel') if channel else 'channel'
            filename = f"youtube_report_{channel_name}_{datetime.now().strftime('%Y%m%d')}.pptx"
            encoded_filename = quote(filename, safe='')
            return Response(
                content=pptx_bytes,
                media_type="application/vnd.openxmlformats-officedocument.presentationml.presentation",
                headers={"Content-Disposition": f"attachment; filename*=UTF-8''{encoded_filename}"}
            )
        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))
    else:
        return {"report": report}


# === 블로그 생성 엔드포인트 ===

@app.post("/api/blog/generate")
async def generate_blog(request: BlogRequest):
    """블로그 포스트 자동 생성"""
    try:
        blog_gen = BlogGenerator(request.gemini_api_key)

        if request.video_id:
            # 특정 영상 기반 블로그 생성
            from database import get_video
            video = get_video(request.video_id)
            if not video:
                raise HTTPException(status_code=404, detail="영상을 찾을 수 없습니다.")

            result = blog_gen.generate_blog_from_video(
                video,
                platform=request.platform,
                theme=request.theme
            )

        else:
            # 채널 분석 기반 블로그 생성
            report = get_latest_report(request.channel_id, 'full_analysis')
            if not report:
                raise HTTPException(status_code=404, detail="분석 보고서를 찾을 수 없습니다.")

            result = blog_gen.generate_blog_from_analysis(
                report['report_data'],
                topic=request.topic,
                platform=request.platform,
                theme=request.theme
            )

        if result.get('success'):
            # DB 저장
            post_id = save_blog_post({
                'channel_id': request.channel_id,
                'video_id': request.video_id,
                'title': result.get('title', ''),
                'content': result.get('content', ''),
                'platform': request.platform,
                'theme': request.theme,
            })
            result['post_id'] = post_id

        return result

    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@app.get("/api/blog/posts")
async def list_blog_posts(channel_id: Optional[str] = None, limit: int = 20):
    """생성된 블로그 포스트 목록"""
    posts = get_blog_posts(channel_id, limit)
    return {"posts": posts, "count": len(posts)}


@app.get("/api/blog/posts/{post_id}")
async def get_blog_post_detail(post_id: int):
    """블로그 포스트 상세"""
    from database import get_connection
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM blog_posts WHERE id = ?', (post_id,))
    row = cursor.fetchone()
    conn.close()

    if not row:
        raise HTTPException(status_code=404, detail="포스트를 찾을 수 없습니다.")

    return {"post": dict(row)}


@app.get("/api/blog/themes")
async def list_themes():
    """사용 가능한 테마 목록"""
    return {
        "themes": [
            {"id": "blue-gray", "name": "블루-그레이 (차분하고 전문적)"},
            {"id": "green-orange", "name": "그린-오렌지 (활기차고 친근)"},
            {"id": "purple-yellow", "name": "퍼플-옐로우 (세련되고 창의적)"},
            {"id": "teal-gray", "name": "틸-라이트그레이 (안정적이고 현대적)"},
            {"id": "terracotta", "name": "테라코타-라이트그레이 (따뜻하고 편안)"},
        ]
    }


# === 영상 관련 엔드포인트 ===

@app.get("/api/videos/{channel_id}")
async def list_channel_videos(channel_id: str, limit: int = 50):
    """채널별 영상 목록"""
    videos = get_videos_by_channel(channel_id, limit)
    return {"videos": videos, "count": len(videos)}


# === 상태 확인 ===

@app.get("/")
async def root():
    """대시보드 페이지 서빙"""
    frontend_path = Path(__file__).parent.parent / "frontend" / "index.html"
    if frontend_path.exists():
        return FileResponse(frontend_path)
    return {"status": "running", "message": "Visit /docs for API documentation"}


@app.get("/api")
async def api_info():
    """API 상태 확인"""
    return {
        "status": "running",
        "name": "YouTube Analytics API",
        "version": "1.0.0",
        "endpoints": {
            "channels": "/api/channels",
            "analyze": "/api/analyze",
            "competitors": "/api/analyze/competitors",
            "blog": "/api/blog/generate",
        }
    }


@app.get("/api/health")
async def health_check():
    """헬스 체크"""
    return {"status": "healthy", "database": "connected"}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8888)
