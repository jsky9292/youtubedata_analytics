from http.server import BaseHTTPRequestHandler
import json
import sys
import os

# 현재 디렉토리를 모듈 경로에 추가
current_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, current_dir)

# FastAPI 앱 가져오기
try:
    from main import app
    FASTAPI_AVAILABLE = True
    IMPORT_ERROR = None
except Exception as e:
    FASTAPI_AVAILABLE = False
    IMPORT_ERROR = str(e)

class handler(BaseHTTPRequestHandler):
    def do_GET(self):
        if not FASTAPI_AVAILABLE:
            self.send_response(500)
            self.send_header('Content-type', 'application/json')
            self.end_headers()
            self.wfile.write(json.dumps({
                "error": IMPORT_ERROR,
                "current_dir": current_dir,
                "sys_path": sys.path[:5]
            }).encode())
            return

        self.send_response(200)
        self.send_header('Content-type', 'application/json')
        self.end_headers()
        self.wfile.write(json.dumps({
            "status": "running",
            "message": "YouTube Analytics API",
            "path": self.path
        }).encode())

    def do_POST(self):
        self.do_GET()
