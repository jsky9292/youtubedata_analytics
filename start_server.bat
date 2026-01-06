@echo off
echo Starting YouTube Analytics Server...
cd /d D:\youtubedata_analytics\backend
python -m uvicorn main:app --host 0.0.0.0 --port 8080 --reload
pause
