"""
YouTube Data API v3 Integration Service
"""
import re
from datetime import datetime
from urllib.parse import unquote, quote
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError


class YouTubeAPIService:
    """YouTube Data API 서비스 클래스"""

    def __init__(self, api_key: str):
        self.api_key = api_key
        self.youtube = build('youtube', 'v3', developerKey=api_key)

    def extract_channel_id(self, url_or_id: str) -> str:
        """URL 또는 ID에서 채널 ID 추출 (한글 핸들 완벽 지원)"""
        original_input = url_or_id.strip()

        # 1. URL 디코딩 (여러 번 인코딩된 경우 대비 - %ED%95%9C%EA%B8%80 -> 한글)
        decoded = original_input
        for _ in range(3):  # 최대 3번 디코딩 시도
            try:
                new_decoded = unquote(decoded, encoding='utf-8')
                if new_decoded == decoded:
                    break
                decoded = new_decoded
            except:
                break

        print(f"[DEBUG] 원본 입력: {original_input}")
        print(f"[DEBUG] 디코딩 후: {decoded}")

        # 2. 이미 채널 ID 형식인 경우 (UC로 시작하는 24자)
        if decoded.startswith('UC') and len(decoded) == 24:
            return decoded

        # 3. @handle 형식 추출 - 더 넓은 문자 범위 지원
        # URL: youtube.com/@핸들 또는 직접 입력: @핸들
        handle_patterns = [
            r'youtube\.com/@([^/?\s&]+)',      # URL 형태
            r'^@([^/?\s&]+)$',                  # @핸들 직접 입력
            r'^([가-힣a-zA-Z0-9_.]+)$',         # 핸들만 입력 (@ 없이)
        ]

        for pattern in handle_patterns:
            match = re.search(pattern, decoded, re.UNICODE)
            if match:
                handle = match.group(1).strip()
                # URL 파라미터 제거
                handle = handle.split('?')[0].split('&')[0]
                print(f"[DEBUG] 추출된 핸들: {handle}")

                if handle:
                    channel_id = self._get_channel_id_by_handle(handle)
                    if channel_id:
                        return channel_id

        # 4. 영상 URL에서 채널 ID 추출 (watch?v= 형식)
        video_match = re.search(r'youtube\.com/watch\?v=([a-zA-Z0-9_-]+)', decoded)
        if video_match:
            video_id = video_match.group(1).split('&')[0]
            print(f"[DEBUG] 영상 URL 감지, video_id: {video_id}")
            try:
                video_info = self.get_video_details(video_id)
                if video_info and video_info.get('channel_id'):
                    print(f"[DEBUG] 영상에서 채널 ID 추출: {video_info['channel_id']}")
                    return video_info['channel_id']
            except Exception as e:
                print(f"[DEBUG] 영상에서 채널 추출 실패: {e}")

        # 5. URL에서 다른 형식 추출
        patterns = [
            (r'youtube\.com/channel/([a-zA-Z0-9_-]{24})', 'channel_id'),
            (r'youtube\.com/c/([^/?\s&]+)', 'custom'),
            (r'youtube\.com/user/([^/?\s&]+)', 'user'),
        ]

        for pattern, pattern_type in patterns:
            match = re.search(pattern, decoded)
            if match:
                identifier = match.group(1)
                if pattern_type == 'channel_id':
                    return identifier
                else:
                    return self._get_channel_id_by_username(identifier)

        # 6. 마지막으로 검색으로 시도
        return self._search_channel(decoded)

    def _get_channel_id_by_handle(self, handle: str) -> str:
        """@handle로 채널 ID 조회 (한글 핸들 지원) - 검색 API 사용"""
        # @ 제거
        clean_handle = handle.lstrip('@').strip()
        print(f"[DEBUG] API 요청 핸들: {clean_handle}")

        # 검색 API로 채널 찾기
        try:
            # @핸들 형태로 검색
            search_query = f"@{clean_handle}"
            print(f"[DEBUG] 검색 쿼리: {search_query}")

            response = self.youtube.search().list(
                part='snippet',
                q=search_query,
                type='channel',
                maxResults=10
            ).execute()

            if response.get('items'):
                # 가장 일치하는 채널 찾기
                for item in response['items']:
                    channel_title = item['snippet']['title']
                    channel_id = item['snippet']['channelId']

                    # 핸들이나 채널명이 일치하는지 확인
                    if clean_handle.lower() in channel_title.lower() or \
                       channel_title.lower() in clean_handle.lower():
                        print(f"[DEBUG] 검색 매칭 성공: {channel_title} ({channel_id})")
                        return channel_id

                # 첫 번째 결과 반환
                first_result = response['items'][0]
                channel_id = first_result['snippet']['channelId']
                print(f"[DEBUG] 검색 첫 결과 사용: {first_result['snippet']['title']} ({channel_id})")
                return channel_id

        except HttpError as e:
            print(f"[DEBUG] 검색 API 실패: {e}")

        raise Exception(f"채널을 찾을 수 없습니다: @{clean_handle}")

    def _get_channel_id_by_username(self, username: str) -> str:
        """username으로 채널 ID 조회"""
        try:
            response = self.youtube.channels().list(
                part='id',
                forUsername=username
            ).execute()

            if response.get('items'):
                return response['items'][0]['id']
        except HttpError:
            pass

        return self._search_channel(username)

    def _search_channel(self, query: str) -> str:
        """채널 검색으로 ID 조회"""
        try:
            response = self.youtube.search().list(
                part='snippet',
                q=query,
                type='channel',
                maxResults=1
            ).execute()

            if response.get('items'):
                return response['items'][0]['snippet']['channelId']
        except HttpError as e:
            raise Exception(f"채널을 찾을 수 없습니다: {query}") from e

        raise Exception(f"채널을 찾을 수 없습니다: {query}")

    def get_channel_info(self, channel_id: str) -> dict:
        """채널 상세 정보 조회"""
        try:
            response = self.youtube.channels().list(
                part='snippet,statistics,contentDetails,brandingSettings',
                id=channel_id
            ).execute()

            if not response.get('items'):
                raise Exception(f"채널을 찾을 수 없습니다: {channel_id}")

            channel = response['items'][0]
            snippet = channel.get('snippet', {})
            statistics = channel.get('statistics', {})
            content_details = channel.get('contentDetails', {})

            return {
                'channel_id': channel_id,
                'channel_name': snippet.get('title'),
                'channel_url': f'https://www.youtube.com/channel/{channel_id}',
                'description': snippet.get('description'),
                'thumbnail_url': snippet.get('thumbnails', {}).get('high', {}).get('url'),
                'subscriber_count': int(statistics.get('subscriberCount', 0)),
                'video_count': int(statistics.get('videoCount', 0)),
                'view_count': int(statistics.get('viewCount', 0)),
                'uploads_playlist_id': content_details.get('relatedPlaylists', {}).get('uploads'),
                'published_at': snippet.get('publishedAt'),
                'country': snippet.get('country'),
                'custom_url': snippet.get('customUrl'),
            }

        except HttpError as e:
            raise Exception(f"YouTube API 오류: {e.reason}") from e

    def get_channel_videos(self, channel_id: str, max_results: int = 50) -> list:
        """채널의 영상 목록 조회"""
        try:
            # 먼저 채널 정보에서 uploads 플레이리스트 ID 가져오기
            channel_info = self.get_channel_info(channel_id)
            uploads_playlist_id = channel_info.get('uploads_playlist_id')

            if not uploads_playlist_id:
                raise Exception("업로드 플레이리스트를 찾을 수 없습니다")

            videos = []
            next_page_token = None

            while len(videos) < max_results:
                # 플레이리스트에서 영상 ID 목록 가져오기
                playlist_response = self.youtube.playlistItems().list(
                    part='contentDetails,snippet',
                    playlistId=uploads_playlist_id,
                    maxResults=min(50, max_results - len(videos)),
                    pageToken=next_page_token
                ).execute()

                video_ids = [
                    item['contentDetails']['videoId']
                    for item in playlist_response.get('items', [])
                ]

                if not video_ids:
                    break

                # 영상 상세 정보 가져오기
                videos_response = self.youtube.videos().list(
                    part='snippet,statistics,contentDetails',
                    id=','.join(video_ids)
                ).execute()

                for video in videos_response.get('items', []):
                    video_data = self._parse_video_data(video, channel_id)
                    videos.append(video_data)

                next_page_token = playlist_response.get('nextPageToken')
                if not next_page_token:
                    break

            return videos

        except HttpError as e:
            raise Exception(f"YouTube API 오류: {e.reason}") from e

    def get_video_details(self, video_id: str) -> dict:
        """단일 영상 상세 정보 조회"""
        try:
            response = self.youtube.videos().list(
                part='snippet,statistics,contentDetails',
                id=video_id
            ).execute()

            if not response.get('items'):
                raise Exception(f"영상을 찾을 수 없습니다: {video_id}")

            video = response['items'][0]
            channel_id = video['snippet']['channelId']

            return self._parse_video_data(video, channel_id)

        except HttpError as e:
            raise Exception(f"YouTube API 오류: {e.reason}") from e

    def _parse_video_data(self, video: dict, channel_id: str) -> dict:
        """API 응답에서 영상 데이터 파싱"""
        snippet = video.get('snippet', {})
        statistics = video.get('statistics', {})
        content_details = video.get('contentDetails', {})

        return {
            'video_id': video['id'],
            'channel_id': channel_id,
            'title': snippet.get('title'),
            'description': snippet.get('description', '')[:500],  # 처음 500자만
            'published_at': snippet.get('publishedAt'),
            'thumbnail_url': snippet.get('thumbnails', {}).get('high', {}).get('url'),
            'duration': self._parse_duration(content_details.get('duration', 'PT0S')),
            'view_count': int(statistics.get('viewCount', 0)),
            'like_count': int(statistics.get('likeCount', 0)),
            'comment_count': int(statistics.get('commentCount', 0)),
            'tags': snippet.get('tags', []),
            'category_id': snippet.get('categoryId'),
        }

    def _parse_duration(self, duration: str) -> str:
        """ISO 8601 기간 형식을 읽기 쉬운 형식으로 변환"""
        # PT1H2M3S -> 1:02:03
        import re
        match = re.match(r'PT(?:(\d+)H)?(?:(\d+)M)?(?:(\d+)S)?', duration)
        if not match:
            return '0:00'

        hours = int(match.group(1) or 0)
        minutes = int(match.group(2) or 0)
        seconds = int(match.group(3) or 0)

        if hours > 0:
            return f'{hours}:{minutes:02d}:{seconds:02d}'
        else:
            return f'{minutes}:{seconds:02d}'

    def search_videos(self, query: str, max_results: int = 25) -> list:
        """영상 검색"""
        try:
            search_response = self.youtube.search().list(
                part='id,snippet',
                q=query,
                type='video',
                maxResults=max_results,
                order='relevance'
            ).execute()

            video_ids = [
                item['id']['videoId']
                for item in search_response.get('items', [])
            ]

            if not video_ids:
                return []

            # 상세 정보 가져오기
            videos_response = self.youtube.videos().list(
                part='snippet,statistics,contentDetails',
                id=','.join(video_ids)
            ).execute()

            videos = []
            for video in videos_response.get('items', []):
                channel_id = video['snippet']['channelId']
                video_data = self._parse_video_data(video, channel_id)
                videos.append(video_data)

            return videos

        except HttpError as e:
            raise Exception(f"YouTube API 오류: {e.reason}") from e

    def get_video_comments(self, video_id: str, max_results: int = 100) -> list:
        """영상 댓글 조회 (분석용)"""
        try:
            response = self.youtube.commentThreads().list(
                part='snippet',
                videoId=video_id,
                maxResults=min(100, max_results),
                order='relevance'
            ).execute()

            comments = []
            for item in response.get('items', []):
                comment = item['snippet']['topLevelComment']['snippet']
                comments.append({
                    'author': comment.get('authorDisplayName'),
                    'text': comment.get('textDisplay'),
                    'like_count': comment.get('likeCount', 0),
                    'published_at': comment.get('publishedAt'),
                })

            return comments

        except HttpError:
            # 댓글이 비활성화된 경우
            return []
