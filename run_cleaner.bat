@echo off
echo Installing dependencies from requirements.txt...
pip install -r requirements.txt
echo.
echo Starting Data Cleaner Pro on localhost:8502...
streamlit run cleaner_app.py --server.port 8502
pause
