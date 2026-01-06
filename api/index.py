import sys
import os

# 현재 디렉토리를 모듈 경로에 추가 (다른 import 전에 실행)
current_dir = os.path.dirname(os.path.abspath(__file__))
if current_dir not in sys.path:
    sys.path.insert(0, current_dir)

# FastAPI 앱 가져오기
from main import app

# Vercel serverless handler (Mangum 사용 가능 시)
try:
    from mangum import Mangum
    handler = Mangum(app)
except ImportError:
    handler = app
