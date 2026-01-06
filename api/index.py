from http.server import BaseHTTPRequestHandler
import json

# FastAPI 앱 가져오기
try:
    from main import app
    FASTAPI_AVAILABLE = True
except Exception as e:
    FASTAPI_AVAILABLE = False
    IMPORT_ERROR = str(e)

class handler(BaseHTTPRequestHandler):
    def do_GET(self):
        if not FASTAPI_AVAILABLE:
            self.send_response(500)
            self.send_header('Content-type', 'application/json')
            self.end_headers()
            self.wfile.write(json.dumps({"error": IMPORT_ERROR}).encode())
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
