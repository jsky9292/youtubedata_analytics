import sys
import os

# 모듈 경로 추가 (다른 import 전에)
current_dir = os.path.dirname(os.path.abspath(__file__))
if current_dir not in sys.path:
    sys.path.insert(0, current_dir)

# FastAPI 앱 가져오기
from main import app

# Mangum을 사용하여 Vercel/AWS Lambda 호환 핸들러 생성
from mangum import Mangum
handler = Mangum(app, lifespan="off")
