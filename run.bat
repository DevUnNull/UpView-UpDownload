@echo off
setlocal
cd /d "%~dp0"

echo ===================================================
echo             UpView - Setup & Khoi chay
echo ===================================================

where python >nul 2>nul
if %errorlevel% neq 0 (
    echo [X] Loi: May tinh cua ban chua cai dat Python hoac chua tich "Add Python to PATH"!
    echo Vui long truy cap https://www.python.org/downloads/ de tai va cai dat.
    echo (Luu y: Nho tich chon vao o "Add python.exe to PATH" khi cai dat)
    pause
    exit /b 1
)

if not exist venv (
    echo [*] Phat hien chua co moi truong ao venv. Dang tu dong tao venv...
    python -m venv venv
    if %errorlevel% neq 0 (
        echo [X] Loi khi tao moi truong ao venv!
        pause
        exit /b 1
    )
    echo [*] Dang cai dat thu vien phu thuoc tu requirements.txt...
    call venv\Scripts\activate.bat
    python -m pip install --upgrade pip
    pip install -r requirements.txt
    echo [OK] Cai dat moi truong hoan tat!
) else (
    call venv\Scripts\activate.bat
)

echo.
echo [*] Dang khoi dong Web Dashboard tai http://127.0.0.1:5050 ...
echo [*] Nhan Ctrl + C de dung server.
echo.
python app.py %*
pause
