@echo off
echo ============================================
echo Project Risk Analysis V2 - VS Code Setup
echo ============================================
py -m venv .venv
if errorlevel 1 (
    echo Python launcher "py" failed. Trying python...
    python -m venv .venv
)
call .venv\Scripts\activate
python -m pip install --upgrade pip
pip install -r requirements.txt
echo.
echo Setup complete.
echo In VS Code select the interpreter:
echo .venv\Scripts\python.exe
pause
