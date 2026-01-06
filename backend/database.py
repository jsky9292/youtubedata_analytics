"""
SQLite Database Manager for YouTube Analytics
"""
import sqlite3
import json
import os
from datetime import datetime
from pathlib import Path

# Vercel 서버리스 환경에서는 /tmp 사용
if os.environ.get('VERCEL'):
    DB_PATH = Path("/tmp/youtube_analytics.db")
else:
    DB_PATH = Path(__file__).parent.parent / "data" / "youtube_analytics.db"
    DB_PATH.parent.mkdir(parents=True, exist_ok=True)


def get_connection():
    """데이터베이스 연결 생성"""
    conn = sqlite3.connect(str(DB_PATH))
    conn.row_factory = sqlite3.Row
    return conn


def init_database():
    """데이터베이스 초기화 - 테이블 생성"""
    conn = get_connection()
    cursor = conn.cursor()

    # 채널 테이블
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS channels (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            channel_id TEXT UNIQUE NOT NULL,
            channel_name TEXT,
            channel_url TEXT,
            subscriber_count INTEGER DEFAULT 0,
            video_count INTEGER DEFAULT 0,
            view_count INTEGER DEFAULT 0,
            description TEXT,
            thumbnail_url TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')

    # 영상 테이블
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS videos (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            video_id TEXT UNIQUE NOT NULL,
            channel_id TEXT NOT NULL,
            title TEXT,
            description TEXT,
            published_at TEXT,
            thumbnail_url TEXT,
            duration TEXT,
            view_count INTEGER DEFAULT 0,
            like_count INTEGER DEFAULT 0,
            comment_count INTEGER DEFAULT 0,
            tags TEXT,
            category_id TEXT,
            performance_score REAL DEFAULT 0,
            classification TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (channel_id) REFERENCES channels(channel_id)
        )
    ''')

    # 분석 보고서 테이블
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS analysis_reports (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            channel_id TEXT NOT NULL,
            report_type TEXT NOT NULL,
            report_data TEXT NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (channel_id) REFERENCES channels(channel_id)
        )
    ''')

    # 경쟁사 분석 테이블
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS competitor_analysis (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            main_channel_id TEXT NOT NULL,
            competitor_channel_id TEXT NOT NULL,
            comparison_data TEXT NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (main_channel_id) REFERENCES channels(channel_id),
            FOREIGN KEY (competitor_channel_id) REFERENCES channels(channel_id)
        )
    ''')

    # 블로그 포스트 테이블
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS blog_posts (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            channel_id TEXT,
            video_id TEXT,
            title TEXT NOT NULL,
            content TEXT NOT NULL,
            platform TEXT DEFAULT 'naver',
            theme TEXT DEFAULT 'blue-gray',
            status TEXT DEFAULT 'draft',
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (channel_id) REFERENCES channels(channel_id),
            FOREIGN KEY (video_id) REFERENCES videos(video_id)
        )
    ''')

    conn.commit()
    conn.close()
    print(f"Database initialized at {DB_PATH}")


# 채널 관련 함수
def save_channel(channel_data: dict) -> int:
    """채널 정보 저장 또는 업데이트"""
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute('''
        INSERT INTO channels (channel_id, channel_name, channel_url, subscriber_count,
                             video_count, view_count, description, thumbnail_url, updated_at)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        ON CONFLICT(channel_id) DO UPDATE SET
            channel_name = excluded.channel_name,
            subscriber_count = excluded.subscriber_count,
            video_count = excluded.video_count,
            view_count = excluded.view_count,
            description = excluded.description,
            thumbnail_url = excluded.thumbnail_url,
            updated_at = excluded.updated_at
    ''', (
        channel_data.get('channel_id'),
        channel_data.get('channel_name'),
        channel_data.get('channel_url'),
        channel_data.get('subscriber_count', 0),
        channel_data.get('video_count', 0),
        channel_data.get('view_count', 0),
        channel_data.get('description'),
        channel_data.get('thumbnail_url'),
        datetime.now().isoformat()
    ))

    conn.commit()
    channel_db_id = cursor.lastrowid
    conn.close()
    return channel_db_id


def get_channel(channel_id: str) -> dict:
    """채널 정보 조회"""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM channels WHERE channel_id = ?', (channel_id,))
    row = cursor.fetchone()
    conn.close()
    return dict(row) if row else None


def get_all_channels() -> list:
    """모든 채널 목록 조회"""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM channels ORDER BY updated_at DESC')
    rows = cursor.fetchall()
    conn.close()
    return [dict(row) for row in rows]


# 영상 관련 함수
def save_video(video_data: dict) -> int:
    """영상 정보 저장 또는 업데이트"""
    conn = get_connection()
    cursor = conn.cursor()

    tags = json.dumps(video_data.get('tags', []), ensure_ascii=False) if video_data.get('tags') else '[]'

    cursor.execute('''
        INSERT INTO videos (video_id, channel_id, title, description, published_at,
                           thumbnail_url, duration, view_count, like_count, comment_count,
                           tags, category_id, performance_score, classification)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ON CONFLICT(video_id) DO UPDATE SET
            title = excluded.title,
            view_count = excluded.view_count,
            like_count = excluded.like_count,
            comment_count = excluded.comment_count,
            performance_score = excluded.performance_score,
            classification = excluded.classification
    ''', (
        video_data.get('video_id'),
        video_data.get('channel_id'),
        video_data.get('title'),
        video_data.get('description'),
        video_data.get('published_at'),
        video_data.get('thumbnail_url'),
        video_data.get('duration'),
        video_data.get('view_count', 0),
        video_data.get('like_count', 0),
        video_data.get('comment_count', 0),
        tags,
        video_data.get('category_id'),
        video_data.get('performance_score', 0),
        video_data.get('classification', 'average')
    ))

    conn.commit()
    video_db_id = cursor.lastrowid
    conn.close()
    return video_db_id


def get_videos_by_channel(channel_id: str, limit: int = 50) -> list:
    """채널별 영상 목록 조회"""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute('''
        SELECT * FROM videos
        WHERE channel_id = ?
        ORDER BY published_at DESC
        LIMIT ?
    ''', (channel_id, limit))
    rows = cursor.fetchall()
    conn.close()
    return [dict(row) for row in rows]


def get_video(video_id: str) -> dict:
    """영상 정보 조회"""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM videos WHERE video_id = ?', (video_id,))
    row = cursor.fetchone()
    conn.close()
    return dict(row) if row else None


# 분석 보고서 관련 함수
def save_analysis_report(channel_id: str, report_type: str, report_data: dict) -> int:
    """분석 보고서 저장"""
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute('''
        INSERT INTO analysis_reports (channel_id, report_type, report_data)
        VALUES (?, ?, ?)
    ''', (channel_id, report_type, json.dumps(report_data, ensure_ascii=False)))

    conn.commit()
    report_id = cursor.lastrowid
    conn.close()
    return report_id


def get_latest_report(channel_id: str, report_type: str = None) -> dict:
    """최신 분석 보고서 조회"""
    conn = get_connection()
    cursor = conn.cursor()

    if report_type:
        cursor.execute('''
            SELECT * FROM analysis_reports
            WHERE channel_id = ? AND report_type = ?
            ORDER BY created_at DESC LIMIT 1
        ''', (channel_id, report_type))
    else:
        cursor.execute('''
            SELECT * FROM analysis_reports
            WHERE channel_id = ?
            ORDER BY created_at DESC LIMIT 1
        ''', (channel_id,))

    row = cursor.fetchone()
    conn.close()

    if row:
        result = dict(row)
        result['report_data'] = json.loads(result['report_data'])
        return result
    return None


# 블로그 포스트 관련 함수
def save_blog_post(post_data: dict) -> int:
    """블로그 포스트 저장"""
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute('''
        INSERT INTO blog_posts (channel_id, video_id, title, content, platform, theme, status)
        VALUES (?, ?, ?, ?, ?, ?, ?)
    ''', (
        post_data.get('channel_id'),
        post_data.get('video_id'),
        post_data.get('title'),
        post_data.get('content'),
        post_data.get('platform', 'naver'),
        post_data.get('theme', 'blue-gray'),
        post_data.get('status', 'draft')
    ))

    conn.commit()
    post_id = cursor.lastrowid
    conn.close()
    return post_id


def get_blog_posts(channel_id: str = None, limit: int = 20) -> list:
    """블로그 포스트 목록 조회"""
    conn = get_connection()
    cursor = conn.cursor()

    if channel_id:
        cursor.execute('''
            SELECT * FROM blog_posts
            WHERE channel_id = ?
            ORDER BY created_at DESC LIMIT ?
        ''', (channel_id, limit))
    else:
        cursor.execute('''
            SELECT * FROM blog_posts
            ORDER BY created_at DESC LIMIT ?
        ''', (limit,))

    rows = cursor.fetchall()
    conn.close()
    return [dict(row) for row in rows]


if __name__ == "__main__":
    init_database()
