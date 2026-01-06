from http.server import BaseHTTPRequestHandler
import json
import sys
import os

# 디버깅: 현재 환경 정보 수집
debug_info = {
    "cwd": os.getcwd(),
    "file": __file__,
    "dir": os.path.dirname(os.path.abspath(__file__)),
    "files_in_dir": [],
    "sys_path": sys.path[:5],
    "import_error": None
}

# 현재 디렉토리 파일 목록
try:
    dir_path = os.path.dirname(os.path.abspath(__file__))
    debug_info["files_in_dir"] = os.listdir(dir_path)[:20]
except Exception as e:
    debug_info["files_in_dir"] = str(e)

# 모듈 경로 추가
current_dir = os.path.dirname(os.path.abspath(__file__))
if current_dir not in sys.path:
    sys.path.insert(0, current_dir)

# main 모듈 import 시도
try:
    from main import app
    debug_info["fastapi_import"] = "success"
except Exception as e:
    debug_info["fastapi_import"] = "failed"
    debug_info["import_error"] = str(e)
    import traceback
    debug_info["traceback"] = traceback.format_exc()

class handler(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.send_header('Content-type', 'application/json')
        self.end_headers()
        self.wfile.write(json.dumps(debug_info, indent=2, default=str).encode())

    def do_POST(self):
        self.do_GET()
