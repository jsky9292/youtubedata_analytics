from http.server import BaseHTTPRequestHandler
import json
import sys
import os
import asyncio
from io import BytesIO
from urllib.parse import parse_qs, urlparse

# 모듈 경로 추가
current_dir = os.path.dirname(os.path.abspath(__file__))
if current_dir not in sys.path:
    sys.path.insert(0, current_dir)

# FastAPI 앱 가져오기
from main import app


class handler(BaseHTTPRequestHandler):
    def _send_cors_headers(self):
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, POST, PUT, DELETE, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')

    def do_OPTIONS(self):
        self.send_response(200)
        self._send_cors_headers()
        self.end_headers()

    def _handle_request(self, method):
        # 요청 정보 추출
        parsed = urlparse(self.path)
        path = parsed.path
        query_string = parsed.query

        # 요청 본문 읽기
        content_length = int(self.headers.get('Content-Length', 0))
        body = self.rfile.read(content_length) if content_length > 0 else b''

        # 헤더 변환
        headers = [(k.lower().encode(), v.encode()) for k, v in self.headers.items()]

        # ASGI scope 구성
        scope = {
            "type": "http",
            "asgi": {"version": "3.0"},
            "http_version": "1.1",
            "method": method,
            "path": path,
            "raw_path": path.encode(),
            "query_string": query_string.encode(),
            "root_path": "",
            "headers": headers,
            "server": ("localhost", 80),
        }

        # 응답 저장 변수
        response_started = False
        response_status = 200
        response_headers = []
        response_body = BytesIO()

        async def receive():
            return {"type": "http.request", "body": body, "more_body": False}

        async def send(message):
            nonlocal response_started, response_status, response_headers

            if message["type"] == "http.response.start":
                response_started = True
                response_status = message["status"]
                response_headers = message.get("headers", [])
            elif message["type"] == "http.response.body":
                response_body.write(message.get("body", b""))

        # FastAPI 앱 실행
        try:
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            loop.run_until_complete(app(scope, receive, send))
            loop.close()
        except Exception as e:
            self.send_response(500)
            self.send_header('Content-Type', 'application/json')
            self._send_cors_headers()
            self.end_headers()
            self.wfile.write(json.dumps({"error": str(e)}).encode())
            return

        # 응답 전송
        self.send_response(response_status)
        for name, value in response_headers:
            if isinstance(name, bytes):
                name = name.decode()
            if isinstance(value, bytes):
                value = value.decode()
            self.send_header(name, value)
        self._send_cors_headers()
        self.end_headers()
        self.wfile.write(response_body.getvalue())

    def do_GET(self):
        self._handle_request("GET")

    def do_POST(self):
        self._handle_request("POST")

    def do_PUT(self):
        self._handle_request("PUT")

    def do_DELETE(self):
        self._handle_request("DELETE")
