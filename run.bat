@echo off
echo Installing dependencies from requirements.txt...
pip install -r requirements.txt
echo.
echo Starting Quant Data Pro on localhost:8501...
streamlit run app.py --server.port 8501
pause
