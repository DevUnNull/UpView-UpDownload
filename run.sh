#!/usr/bin/env bash
set -e
cd "$(dirname "$0")"

# Tự động tạo venv và cài đặt dependencies nếu chưa có
if [ ! -d "venv" ]; then
    echo "[*] Phát hiện chưa có môi trường ảo venv. Đang tự động khởi tạo..."
    python3 -m venv venv || {
        echo "[X] Lỗi: Không thể tạo venv bằng python3. Vui lòng kiểm tra Python 3 đã được cài đặt."
        exit 1
    }
    echo "[*] Đang nâng cấp pip và cài đặt thư viện từ requirements.txt..."
    ./venv/bin/pip install --upgrade pip
    ./venv/bin/pip install -r requirements.txt
    echo "[✓] Khởi tạo môi trường ảo thành công!"
fi

source venv/bin/activate
python3 app.py "$@"

