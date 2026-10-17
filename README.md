# UpView - Automated View Bot (Web Dashboard)

Hệ thống tự động hóa tăng lượt truy cập (view) chất lượng cao bằng Selenium Headless Chrome với giao diện Web Dashboard thời gian thực.

---

## 🌟 Các Tính Năng Nổi Bật

- **Giao Diện Web Hiện Đại**: Chạy mượt mà trên mọi trình duyệt (Chrome, Safari...), hiển thị sắc nét với giao diện Dark Mode chuẩn công nghệ.
- **Thống Kê Thời Gian Thực**: Theo dõi tổng số lượt view, số lượt thành công, **lượt tải (downloads)**, thất bại và tỉ lệ hoàn thành (%) trực tiếp.
- **Tự Động Kích Hoạt Tải Về (Auto-Click Download)**: Tự động tìm nút Download trên Itch.io, vượt modal quyên góp và click tệp game để kích hoạt tăng lượt tải trên server Itch.io.
- **Chặn Lưu File Rác Đầy Ổ Cứng**: Sử dụng thư mục tạm thời tự hủy ngay sau mỗi phiên, không tốn dung lượng ổ đĩa.
- **Chống Phát Hiện Bot & Unique View (Itch.io Optimized)**:
  - Chế độ Ẩn danh (Incognito Mode) xóa sạch cookie, session, local storage.
  - Vô hiệu hóa cờ `navigator.webdriver` (Stealth Mode) qua Chrome DevTools Protocol.
  - Xoay vòng User-Agent đa dạng (Windows, macOS, Linux) & kích thước màn hình ngẫu nhiên.
  - Hỗ trợ Proxy xoay vòng IP chống lọc dải mạng.
- **Thanh Tiến Độ Trực Quan (Progress Bar)**: Cập nhật động theo từng lượt view.
- **Live Terminal Console**: Hiển thị luồng log chi tiết từng giây với màu sắc phân biệt trực quan.
- **Giả Lập Hành Vi Người Thật (Human Simulation)**:
  - Thời gian dừng ngẫu nhiên trên trang (Stay duration 8s - 15s).
  - Tự động cuộn trang (Smooth scrolling) kích hoạt sự kiện đọc và analytics.
- **Headless Chrome**: Tự động chạy ngầm không chiếm màn hình, tiết kiệm tối đa CPU/RAM.
- **Điều Khiển Linh Hoạt**: Bắt đầu và Dừng khẩn cấp bất kỳ lúc nào chỉ với 1 click.

---

## 📁 Cấu Trúc Dự Án

```
UpView/
├── app.py                # Backend Web Server (Flask + Selenium Worker)
├── run.sh                # Script khởi chạy nhanh hệ thống Web Dashboard
├── requirements.txt      # Danh sách thư viện phụ thuộc
├── templates/
│   └── index.html        # Giao diện Web Dashboard (HTML5, CSS3, JS)
├── view_bot.py           # Bản chạy độc lập dòng lệnh (CLI)
└── venv/                 # Môi trường ảo Python
```

---

## 🚀 Hướng Dẫn Sử Dụng

### 1. Khởi chạy Web Dashboard
Bạn chỉ cần mở Terminal tại thư mục dự án và chạy:
```bash
./run.sh
```
Trình duyệt sẽ tự động mở trang quản trị tại: **[http://127.0.0.1:5050](http://127.0.0.1:5050)**

### 2. Thiết lập & Cày view
1. Nhập đường dẫn trang web mục tiêu vào ô **Link Website Mục Tiêu (URL)**.
2. Điều chỉnh số lượng view và khoảng thời gian xem (mặc định: 5s - 10s).
3. Bật/tắt tùy chọn **Chạy ngầm (Headless)** hoặc **Giả lập cuộn trang**.
4. Bấm **▶ Bắt Đầu Chạy** để khởi động chiến dịch.
5. Theo dõi tiến trình trực tiếp trên thanh trạng thái và bảng nhật ký.
6. Bấm **■ Dừng Lại** bất cứ lúc nào nếu muốn ngắt chiến dịch.
