# 🚀 UpView - Automated View & Engagement Bot (Web Dashboard)

> Hệ thống tự động hóa tăng lượt truy cập (Views), lượt chơi game (Browser Plays), lượt tải (Downloads) và bình luận (Comments) chất lượng cao bằng Selenium Headless Chrome với giao diện Web Dashboard thời gian thực.

---

## 📋 Mục Lục
- [🌟 Các Tính Năng Nổi Bật](#-các-tính-năng-nổi-bật)
- [📁 Cấu Trúc Dự Án](#-cấu-trúc-dự-án)
- [⚙️ Yêu Cầu Tiên Quyết (Prerequisites)](#️-yêu-cầu-tiên-quyết-prerequisites)
- [⚡ Cách 1: Khởi Chạy Tự Động 1-Click (Khuyên Dùng)](#-cách-1-khởi-chạy-tự-động-1-click-khuyên-dùng)
- [🛠️ Cách 2: Cài Đặt Thủ Công Từ Đầu (Manual Setup A - Z)](#️-cách-2-cài-đặt-thủ-công-từ-đầu-manual-setup-a---z)
  - [Dành cho Windows](#1-dành-cho-windows-cmd--powershell)
  - [Dành cho macOS](#2-dành-cho-macos)
  - [Dành cho Linux (Ubuntu / Debian / VPS)](#3-dành-cho-linux-ubuntu--debian--vps)
- [🐳 Cách 3: Chạy Bằng Docker (Tiện Lợi Nhất Cho VPS / Server)](#-cách-3-chạy-bằng-docker-tiện-lợi-nhất-cho-vps--server)
- [💻 Cách 4: Chạy Bằng Dòng Lệnh CLI (Không Cần Web)](#-cách-4-chạy-bằng-dòng-lệnh-cli-không-cần-web)
- [🎮 Hướng Dẫn Sử Dụng Web Dashboard](#-hướng-dẫn-sử-dụng-web-dashboard)
- [❓ Xử Lý Lỗi Thường Gặp (Troubleshooting & FAQ)](#-xử-lý-lỗi-thường-gặp-troubleshooting--faq)

---

## 🌟 Các Tính Năng Nổi Bật

- **Giao Diện Web Hiện Đại**: Bảng điều khiển công nghệ Dark Mode, hiển thị trực quan và mượt mà trên mọi trình duyệt.
- **Thống Kê Thời Gian Thực**: Theo dõi tổng lượt view, thành công, **lượt chơi (plays)**, **lượt tải (downloads)**, **bình luận (comments)**, thất bại và tỉ lệ hoàn thành (%) trực tiếp.
- **Tự Động Kích Hoạt Chơi Game (Auto-Play / Run Game)**: Tự động định vị nút "Run game", "Play game", "Restore game", tải iframe WebGL/HTML5 và kích hoạt tăng lượt chơi (Browser Plays) trên server Itch.io.
- **Tự Động Gửi Bình Luận (Auto-Comment Itch.io)**: Tự động cuộn trang, điền nội dung ngẫu nhiên vào ô bình luận và gửi (hỗ trợ nạp Cookie phiên đăng nhập tài khoản).
- **Tự Động Kích Hoạt Tải Về (Auto-Click Download)**: Tự động tìm nút Download trên Itch.io, vượt qua modal quyên góp và click tệp game để kích hoạt tăng lượt tải trên server.
- **Chặn Lưu File Rác Đầy Ổ Cứng**: Dùng thư mục tạm thời tự hủy ngay sau mỗi phiên, không chiếm dung lượng ổ đĩa.
- **Chống Phát Hiện Bot & Unique View (Itch.io Optimized)**:
  - Chế độ Ẩn danh (Incognito Mode) xóa sạch cookie, cache và local storage sau mỗi session.
  - Vô hiệu hóa cờ `navigator.webdriver` (Stealth Mode) qua Chrome DevTools Protocol.
  - Xoay vòng User-Agent đa dạng (Windows, macOS, Linux) & kích thước màn hình ngẫu nhiên.
  - Hỗ trợ Proxy xoay vòng IP chống rate-limit.
- **Giả Lập Hành Vi Người Thật (Human Simulation)**:
  - Thời gian dừng ngẫu nhiên trên trang (Stay duration tùy chỉnh).
  - Tự động cuộn trang (Smooth scrolling) kích hoạt sự kiện đọc và analytics.
- **Live Terminal Console**: Hiển thị luồng log chi tiết từng giây với màu sắc phân biệt trực quan.
- **Điều Khiển Linh Hoạt**: Bắt đầu và Dừng khẩn cấp bất kỳ lúc nào chỉ với 1 click.

---

## 📁 Cấu Trúc Dự Án

```text
UpView/
├── app.py                # Backend Web Server (Flask + Selenium Worker)
├── run.sh                # Script khởi chạy tự động cho macOS / Linux (tự tạo venv & cài thư viện)
├── run.bat               # Script khởi chạy tự động cho Windows (tự tạo venv & cài thư viện)
├── requirements.txt      # Danh sách thư viện Python cần thiết
├── Dockerfile            # Cấu hình đóng gói Docker chạy trên Server/VPS
├── templates/
│   └── index.html        # Giao diện Web Dashboard (HTML5, CSS3, JS)
├── view_bot.py           # Bản chạy độc lập dòng lệnh (CLI mode)
├── .gitignore            # Danh sách file/thư mục bỏ qua khi đẩy lên Git
└── README.md             # Tài liệu hướng dẫn sử dụng
```

---

## ⚙️ Yêu Cầu Tiên Quyết (Prerequisites)

Trước khi bắt đầu cài đặt, máy tính của bạn cần có sẵn:

1. **Google Chrome**:
   - Vì tool sử dụng Selenium để điều khiển trình duyệt Chrome thực tế nhằm vượt qua cơ chế chống bot, máy tính của bạn **bắt buộc phải có sẵn Google Chrome**.
   - 👉 [Tải Google Chrome chính thức tại đây](https://www.google.com/chrome/) nếu máy bạn chưa có.
2. **Python 3.8 đến 3.12+**:
   - 👉 [Tải Python chính thức tại đây](https://www.python.org/downloads/).
   - ⚠️ **LƯU Ý CỰC KỲ QUAN TRỌNG TRÊN WINDOWS**: Trong quá trình cài đặt Python, ở màn hình đầu tiên, bạn **BẮT BUỘC PHẢI TÍCH CHỌN** vào ô `Add python.exe to PATH` (hoặc `Add Python to environment variables`) trước khi bấm Install.
3. **Git (Tùy chọn)**:
   - Dùng để tải mã nguồn bằng lệnh `git clone`. Nếu không có Git, bạn có thể tải file `.zip` từ Github về và giải nén bình thường.

---

## ⚡ Cách 1: Khởi Chạy Tự Động 1-Click (Khuyên Dùng)

Dự án đã tích hợp sẵn script tự động kiểm tra, khởi tạo môi trường ảo `venv`, tự động cài đặt toàn bộ thư viện trong `requirements.txt` và khởi chạy server. Bạn không cần gõ từng lệnh thủ công.

### Trên macOS / Linux:
1. Mở Terminal và di chuyển vào thư mục dự án `UpView`:
   ```bash
   cd /path/to/UpView
   ```
2. Cấp quyền thực thi cho file script (chỉ cần làm lần đầu tiên):
   ```bash
   chmod +x run.sh
   ```
3. Khởi chạy:
   ```bash
   ./run.sh
   ```
4. Mở trình duyệt truy cập: **[http://127.0.0.1:5050](http://127.0.0.1:5050)**

---

### Trên Windows:
1. Mở thư mục `UpView` vừa tải về.
2. **Nhấp đúp chuột vào file `run.bat`** (hoặc mở Command Prompt gõ `run.bat`).
3. Script sẽ tự động tạo `venv`, cài thư viện và bật server.
4. Mở trình duyệt truy cập: **[http://127.0.0.1:5050](http://127.0.0.1:5050)**

---

## 🛠️ Cách 2: Cài Đặt Thủ Công Từ Đầu (Manual Setup A - Z)

Nếu bạn muốn tự thiết lập từng bước hoặc script tự động gặp hạn chế về phân quyền trên máy:

### 1. Dành cho Windows (CMD / PowerShell)

1. **Mở Command Prompt (CMD) hoặc PowerShell** và chuyển vào thư mục dự án:
   ```cmd
   cd C:\duong-dan-toi\UpView
   ```

2. **Kiểm tra Python đã cài đặt thành công:**
   ```cmd
   python --version
   ```
   *(Đảm bảo hiển thị phiên bản Python 3.8 trở lên)*

3. **Khởi tạo môi trường ảo (Virtual Environment):**
   ```cmd
   python -m venv venv
   ```

4. **Kích hoạt môi trường ảo:**
   - Nếu dùng **Command Prompt (CMD)**:
     ```cmd
     venv\Scripts\activate.bat
     ```
   - Nếu dùng **PowerShell**:
     ```powershell
     .\venv\Scripts\Activate.ps1
     ```
     *(Nếu PowerShell báo lỗi `execution of scripts is disabled`, hãy mở PowerShell và chạy lệnh `Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass`, sau đó chạy lại lệnh kích hoạt)*

5. **Cài đặt các thư viện cần thiết:**
   ```cmd
   python -m pip install --upgrade pip
   pip install -r requirements.txt
   ```

6. **Khởi chạy ứng dụng:**
   ```cmd
   python app.py
   ```

7. Mở trình duyệt và truy cập: **[http://127.0.0.1:5050](http://127.0.0.1:5050)**

---

### 2. Dành cho macOS

1. **Mở Terminal** và chuyển vào thư mục dự án:
   ```bash
   cd ~/Documents/UpView
   ```

2. **Kiểm tra Python:**
   ```bash
   python3 --version
   ```

3. **Khởi tạo môi trường ảo:**
   ```bash
   python3 -m venv venv
   ```

4. **Kích hoạt môi trường ảo:**
   ```bash
   source venv/bin/activate
   ```

5. **Nâng cấp pip và cài đặt thư viện:**
   ```bash
   pip install --upgrade pip
   pip install -r requirements.txt
   ```

6. **Khởi chạy ứng dụng:**
   ```bash
   python3 app.py
   ```

7. Mở trình duyệt và truy cập: **[http://127.0.0.1:5050](http://127.0.0.1:5050)**

---

### 3. Dành cho Linux (Ubuntu / Debian / VPS)

Nếu chạy trên máy tính Linux hoặc VPS (Ubuntu/Debian) chưa có gì:

1. **Cập nhật hệ thống và cài đặt Python, venv, Google Chrome:**
   ```bash
   sudo apt-get update && sudo apt-get install -y python3 python3-pip python3-venv wget curl unzip libnss3 libgconf-2-4 libfontconfig1
   
   # Cài đặt Google Chrome Stable chính thức
   wget -q -O - https://dl-ssl.google.com/linux/linux_signing_key.pub | sudo gpg --dearmor -o /usr/share/keyrings/google-chrome.gpg
   echo "deb [arch=amd64 signed-by=/usr/share/keyrings/google-chrome.gpg] http://dl.google.com/linux/chrome/deb/ stable main" | sudo tee /etc/apt/sources.list.d/google-chrome.list
   sudo apt-get update && sudo apt-get install -y google-chrome-stable
   ```

2. **Chuyển vào thư mục dự án và tạo môi trường ảo:**
   ```bash
   cd UpView
   python3 -m venv venv
   source venv/bin/activate
   pip install --upgrade pip
   pip install -r requirements.txt
   ```

3. **Khởi chạy ứng dụng:**
   ```bash
   python3 app.py
   ```

4. Nếu chạy trên VPS, bạn có thể truy cập qua IP công khai của VPS: **`http://<IP_VPS>:5050`**

---

## 🐳 Cách 3: Chạy Bằng Docker (Tiện Lợi Nhất Cho VPS / Server)

Nếu máy bạn đã cài sẵn **Docker**, bạn **KHÔNG CẦN** cài đặt Python hay Google Chrome lên máy chính. Dockerfile đã được tích hợp sẵn hệ điều hành Linux, Google Chrome Stable mới nhất, Python 3.11 và toàn bộ dependencies.

1. **Build Docker Image:**
   ```bash
   docker build -t upview .
   ```

2. **Khởi chạy Container chạy ngầm:**
   ```bash
   docker run -d --name upview_app -p 5050:5050 --restart always upview
   ```

3. **Truy cập Dashboard:**
   Mở trình duyệt vào **[http://localhost:5050](http://localhost:5050)** (hoặc `http://<IP_VPS>:5050`).

4. **Quản lý Docker:**
   - Xem log hoạt động: `docker logs -f upview_app`
   - Dừng container: `docker stop upview_app`
   - Xóa container: `docker rm upview_app`

---

## 💻 Cách 4: Chạy Bằng Dòng Lệnh CLI (Không Cần Web)

Nếu bạn không muốn mở giao diện web mà muốn chạy nhanh trực tiếp trên terminal:

```bash
# Cú pháp:
python view_bot.py <URL_WEBSITE> [TỔNG_SỐ_VIEW] [THỜI_GIAN_MIN_GIÂY] [THỜI_GIAN_MAX_GIÂY]

# Ví dụ: Tăng 20 view cho game trên Itch.io, mỗi phiên ở lại từ 8 đến 15 giây:
python view_bot.py https://mygame.itch.io/demo-game 20 8 15
```

---

## 🎮 Hướng Dẫn Sử Dụng Web Dashboard

Sau khi mở trang `http://127.0.0.1:5050`:

1. **Link Website Mục Tiêu (URL)**: Dán link trang web hoặc link game Itch.io cần tăng tương tác.
2. **Số Lượt View**: Nhập tổng số session cần chạy (ví dụ: `50`).
3. **Thời Gian Xem (giây)**: Đặt thời gian ngẫu nhiên ở lại trang (ví dụ: Tối thiểu `8` giây, Tối đa `15` giây).
4. **Các Tùy Chọn Tính Năng**:
   - `Chạy ngầm (Headless Mode)`: Ẩn hoàn toàn cửa sổ trình duyệt để tiết kiệm RAM/CPU. Nếu muốn nhìn thấy trình duyệt Chrome tự lướt thật thì bỏ tick chọn này.
   - `Giả lập cuộn trang`: Tự động cuộn lên xuống mượt mà như người đọc thật.
   - `Tự động chơi game (Itch.io Play)`: Tự bấm "Run game" / "Play game" và nạp WebGL iframe để tính Browser Play.
   - `Tự động tải về (Itch.io Download)`: Tự bấm nút Download, vượt modal quyên góp để tính lượt Download.
   - `Tự động gửi bình luận (Itch.io Comment)`: Nhập danh sách bình luận (mỗi dòng một câu) và dán Cookie tài khoản Itch.io nếu muốn đăng nhập bình luận tự động.
   - `Danh sách Proxy`: Nhập danh sách Proxy (dạng `ip:port` hoặc `http://user:pass@ip:port`, mỗi dòng 1 proxy) để tự động xoay IP giữa các phiên.
5. **Điều Khiển**:
   - Bấm **▶ Bắt Đầu Chạy** để khởi động chiến dịch.
   - Bấm **■ Dừng Lại** bất kỳ lúc nào nếu muốn ngắt phiên.
   - Theo dõi thanh tiến độ và hộp **Live Terminal Log** bên dưới.

---

## ❓ Xử Lý Lỗi Thường Gặp (Troubleshooting & FAQ)

### 1. Lỗi: `python: command not found` hoặc `python is not recognized as an internal or external command`
- **Nguyên nhân**: Máy tính chưa cài Python hoặc khi cài trên Windows quên chưa tích chọn `Add python.exe to PATH`.
- **Cách khắc phục**:
  - Gỡ cài đặt và tải lại Python từ [python.org](https://www.python.org/downloads/).
  - Trong bước cài đặt đầu tiên, **chú ý tích chọn vào ô `Add Python to PATH`**.

---

### 2. Lỗi PowerShell: `File ... Activate.ps1 cannot be loaded because running scripts is disabled on this system`
- **Nguyên nhân**: Chính sách bảo mật mặc định của Windows hạn chế chạy script PowerShell.
- **Cách khắc phục**:
  - Mở PowerShell và nhập lệnh sau:
    ```powershell
    Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass
    ```
  - Sau đó chạy lại lệnh kích hoạt: `.\venv\Scripts\Activate.ps1`. Hoặc đơn giản là dùng `run.bat` hay Command Prompt (CMD).

---

### 3. Lỗi: `WebDriverException: Message: Google Chrome not found` hoặc `chrome not reachable`
- **Nguyên nhân**: Máy tính chưa cài đặt trình duyệt Google Chrome chính thức hoặc phiên bản quá cũ.
- **Cách khắc phục**:
  - Tải và cài đặt Google Chrome bản mới nhất từ [google.com/chrome](https://www.google.com/chrome/).
  - Trên Linux (VPS): Cài đặt `google-chrome-stable` theo hướng dẫn tại [Mục 3 của Cách 2](#3-dành-cho-linux-ubuntu--debian--vps).

---

### 4. Lỗi trên macOS / Linux: `Permission denied: ./run.sh`
- **Cách khắc phục**: Cấp quyền thực thi cho file bằng lệnh:
  ```bash
  chmod +x run.sh
  ```

---

### 5. Lỗi: `OSError: [Errno 48] Address already in use: Port 5050`
- **Nguyên nhân**: Cổng 5050 đang bị ứng dụng khác hoặc một phiên chạy trước đó chiếm dụng.
- **Cách khắc phục**:
  - Tắt tiến trình cũ đang chiếm port 5050:
    - Trên macOS / Linux: `lsof -i :5050` sau đó `kill -9 <PID>`
    - Trên Windows CMD: `netstat -ano | findstr :5050` sau đó `taskkill /PID <PID> /F`
  - Hoặc mở file `app.py`, sửa dòng `PORT = 5050` thành cổng khác (ví dụ `5060`).

---

### 6. Tôi muốn nhìn thấy trình duyệt bật lên để kiểm tra hoạt động có được không?
- **Hoàn toàn được**: Trên giao diện Web Dashboard, bạn chỉ cần **BỎ TICK** ô chọn **"Chạy ngầm (Headless Mode)"** trước khi bấm **Bắt Đầu Chạy**. Khi đó, cửa sổ trình duyệt Chrome sẽ mở lên trực tiếp trên màn hình để bạn quan sát từng thao tác cuộn chuột và click.

---

## 🔒 Tuyên Bố Miễn Trừ Trách Nhiệm (Disclaimer)
Dự án được phát triển nhằm mục đích nghiên cứu kiểm thử tự động hóa web (Automated Web Testing) và tối ưu hóa hiệu năng ứng dụng. Người sử dụng chịu hoàn toàn trách nhiệm về mục đích và hành vi sử dụng công cụ tuân thủ theo điều khoản dịch vụ của các nền tảng liên quan.
