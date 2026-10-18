#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Tên tool: UpView Bot Web Dashboard (Itch.io & Anti-Detection & Auto-Download & Auto-Comment)
Mô tả: Hệ thống cày view, tự động click download và gửi bình luận chống phát hiện bot trên Itch.io.
"""

import os
import sys
import time
import random
import threading
import warnings
import tempfile
import shutil
import webbrowser
from flask import Flask, render_template, request, jsonify

# Tắt cảnh báo
warnings.filterwarnings("ignore")

try:
    from selenium import webdriver
    from selenium.webdriver.common.by import By
    from selenium.webdriver.support.ui import WebDriverWait
    from selenium.webdriver.support import expected_conditions as EC
    from selenium.webdriver.chrome.service import Service
    from webdriver_manager.chrome import ChromeDriverManager
    from selenium.webdriver.chrome.options import Options
    from selenium.common.exceptions import WebDriverException, TimeoutException
except ImportError:
    print("[-] Thiếu thư viện. Hãy cài đặt: pip install selenium webdriver-manager flask")
    sys.exit(1)

app = Flask(__name__)
app.config['TEMPLATES_AUTO_RELOAD'] = True

# Danh sách User-Agent đa dạng giả lập nhiều dòng máy & trình duyệt thực
USER_AGENTS = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/128.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/127.0.0.0 Safari/537.36 Edg/127.0.0.0",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.5 Safari/605.1.15",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/128.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:129.0) Gecko/20100101 Firefox/129.0",
    "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36",
    "Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:128.0) Gecko/20100101 Firefox/128.0",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 14_5) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/127.0.0.0 Safari/537.36"
]

# Kích thước màn hình phổ biến ngẫu nhiên
VIEWPORT_SIZES = [
    (1366, 768),
    (1440, 900),
    (1920, 1080),
    (1280, 800),
    (1536, 864),
    (1600, 900)
]

# Danh sách bình luận mẫu cho Itch.io
SAMPLE_COMMENTS = [
    "Game rất hay và cuốn hút! Chúc dự án phát triển tốt nhé.",
    "Đồ họa và cơ chế chơi tuyệt vời, rất đáng trải nghiệm!",
    "Mình rất thích ý tưởng này, cố lên tác giả ơi!",
    "Trải nghiệm mượt mà, gameplay sáng tạo.",
    "Awesome game! Really enjoyed playing it.",
    "The art style and soundtrack are amazing! Keep up the great work.",
    "Great concept and execution. Looking forward to future updates!",
    "Chơi rất cuốn, ủng hộ tác giả ra thêm nhiều màn mới nhé!"
]

# Quản lý trạng thái bot
bot_state = {
    "is_running": False,
    "current_view": 0,
    "total_views": 0,
    "success_count": 0,
    "fail_count": 0,
    "download_count": 0,
    "comment_count": 0,
    "logs": ["[✓] Hệ thống Web Dashboard đã khởi động sẵn sàng."],
    "current_driver": None,
    "lock": threading.Lock()
}

def add_log(message):
    with bot_state["lock"]:
        timestamp = time.strftime("[%H:%M:%S] ")
        bot_state["logs"].append(timestamp + message)
        if len(bot_state["logs"]) > 250:
            bot_state["logs"].pop(0)

def simulate_download_action(driver):
    """
    Tự động định vị và click nút Download trên Itch.io:
    1. Tìm nút Download / Download Now trên trang chủ game.
    2. Vượt popup quyên góp nếu có ("No thanks, just take me to the downloads").
    3. Click nút tải tệp cụ thể để server Itch.io ghi nhận lượt Download.
    """
    try:
        wait = WebDriverWait(driver, 8)
        download_xpath = (
            "//a[contains(@class, 'download_btn') or contains(@class, 'buy_btn') or "
            "contains(translate(text(), 'DOWNLOAD', 'download'), 'download')] | "
            "//button[contains(@class, 'download_btn') or contains(@class, 'buy_btn') or "
            "contains(translate(text(), 'DOWNLOAD', 'download'), 'download')]"
        )

        btn = None
        try:
            btn = wait.until(EC.element_to_be_clickable((By.XPATH, download_xpath)))
        except Exception:
            pass

        if not btn:
            css_buttons = driver.find_elements(By.CSS_SELECTOR, ".download_btn, .buy_btn, .btn_download, a[href*='/download/']")
            for b in css_buttons:
                if b.is_displayed():
                    btn = b
                    break

        if btn:
            add_log("[*] Đã tìm thấy nút Download, đang tiến hành click...")
            driver.execute_script("arguments[0].scrollIntoView({behavior: 'smooth', block: 'center'});", btn)
            time.sleep(1.0)
            try:
                btn.click()
            except Exception:
                driver.execute_script("arguments[0].click();", btn)

            time.sleep(random.uniform(2.0, 3.5))

            # Xử lý modal quyên góp nếu có ("No thanks, just take me to the downloads")
            try:
                direct_links = driver.find_elements(
                    By.XPATH,
                    "//a[contains(@class, 'direct_download_btn') or "
                    "contains(text(), 'No thanks') or "
                    "contains(translate(text(), 'DOWNLOADS', 'downloads'), 'take me to the downloads')]"
                )
                for dl in direct_links:
                    if dl.is_displayed():
                        add_log("[*] Phát hiện trang xác nhận tải, chuyển tiếp đến tệp tải về...")
                        try:
                            dl.click()
                        except Exception:
                            driver.execute_script("arguments[0].click();", dl)
                        time.sleep(random.uniform(2.0, 3.0))
                        break
            except Exception:
                pass

            # Xử lý nút tải file cụ thể nếu ở trang /download/...
            try:
                file_downloads = driver.find_elements(
                    By.XPATH,
                    "//a[contains(@class, 'download_btn') or contains(@href, '/file/') or contains(@class, 'button_download')]"
                )
                for fd in file_downloads:
                    if fd.is_displayed():
                        add_log("[*] Kích hoạt tải tệp game...")
                        try:
                            fd.click()
                        except Exception:
                            driver.execute_script("arguments[0].click();", fd)
                        time.sleep(random.uniform(2.5, 4.0))
                        break
            except Exception:
                pass

            with bot_state["lock"]:
                bot_state["download_count"] += 1
            add_log("[📥] Đã kích hoạt lượt Download thành công lên server Itch.io!")
            return True
        else:
            add_log("[-] Không tìm thấy nút Download hiển thị trên trang này.")
            return False
    except Exception as e:
        err = str(e).splitlines()[0] if str(e).splitlines() else "Lỗi không xác định"
        add_log(f"[!] Sự cố khi click nút Download: {err}")
        return False

def simulate_comment_action(driver, custom_comments=None):
    """
    Hàm tự động cuộn xuống khung bình luận, nhập nội dung ngẫu nhiên và bấm gửi trên Itch.io.
    """
    try:
        # Cuộn trang xuống khu vực bình luận
        driver.execute_script("window.scrollTo({top: document.body.scrollHeight, behavior: 'smooth'});")
        time.sleep(2.0)

        # Định vị ô textarea bình luận của Itch.io
        comment_selectors = [
            "textarea[name='body']",
            ".comment_form textarea",
            "#comment_body",
            ".community_post_form textarea",
            "textarea"
        ]

        comment_box = None
        for sel in comment_selectors:
            try:
                boxes = driver.find_elements(By.CSS_SELECTOR, sel)
                for b in boxes:
                    if b.is_displayed() and b.is_enabled():
                        comment_box = b
                        break
                if comment_box:
                    break
            except Exception:
                continue

        if comment_box:
            comments_pool = custom_comments if (custom_comments and len(custom_comments) > 0) else SAMPLE_COMMENTS
            comment_text = random.choice(comments_pool)

            driver.execute_script("arguments[0].scrollIntoView({behavior: 'smooth', block: 'center'});", comment_box)
            time.sleep(1.0)

            try:
                comment_box.click()
            except Exception:
                pass

            comment_box.clear()
            comment_box.send_keys(comment_text)
            display_txt = comment_text[:40] + "..." if len(comment_text) > 40 else comment_text
            add_log(f"[*] Đã nhập bình luận: \"{display_txt}\"")
            time.sleep(1.2)

            submit_selectors = [
                "input[type='submit'][value*='Post']",
                "button[type='submit']",
                ".comment_form button",
                ".post_comment_btn",
                "input[type='submit']"
            ]

            submit_btn = None
            for s_sel in submit_selectors:
                try:
                    btns = driver.find_elements(By.CSS_SELECTOR, s_sel)
                    for btn in btns:
                        if btn.is_displayed() and btn.is_enabled():
                            submit_btn = btn
                            break
                    if submit_btn:
                        break
                except Exception:
                    continue

            if submit_btn:
                try:
                    submit_btn.click()
                except Exception:
                    driver.execute_script("arguments[0].click();", submit_btn)

                with bot_state["lock"]:
                    bot_state["comment_count"] += 1
                add_log("[💬] Đã gửi bình luận thành công lên Itch.io!")
                time.sleep(2.5)
                return True
            else:
                add_log("[-] Không tìm thấy nút gửi bình luận (Submit).")
                return False
        else:
            add_log("[-] Khung bình luận chưa khả dụng (Trang tắt bình luận hoặc yêu cầu đăng nhập tài khoản Itch.io).")
            return False
    except Exception as e:
        err = str(e).splitlines()[0] if str(e).splitlines() else "Lỗi không xác định"
        add_log(f"[!] Không thể gửi bình luận: {err}")
        return False

def bot_worker(url, total_sessions, min_wait, max_wait, is_headless, do_scroll, do_download, do_comment=False, custom_comments=None, proxies_list=None):
    add_log(f"[*] Bắt đầu chiến dịch: {url}")
    dl_status = "Bật" if do_download else "Tắt"
    cm_status = "Bật" if do_comment else "Tắt"
    add_log(f"[*] Cấu hình: {total_sessions} views | Chờ: {min_wait}s - {max_wait}s | Download: {dl_status} | Comment: {cm_status}")
    if proxies_list:
        add_log(f"[*] Đã nạp danh sách {len(proxies_list)} Proxy xoay vòng IP.")
    else:
        add_log("[*] Chạy chế độ Direct IP (Mỗi lượt sử dụng Incognito Profile độc lập).")

    for i in range(1, total_sessions + 1):
        if not bot_state["is_running"]:
            add_log("[!] Đã dừng chiến dịch theo yêu cầu người dùng.")
            break

        with bot_state["lock"]:
            bot_state["current_view"] = i

        driver = None
        temp_dl_dir = None
        try:
            # Tạo thư mục tải tạm thời riêng biệt cho phiên này (tự động xóa sau khi xong)
            temp_dl_dir = tempfile.mkdtemp(prefix="itch_dl_")

            chrome_options = Options()
            if is_headless:
                chrome_options.add_argument("--headless=new")
            
            # --- CÁC CỜ CHỐNG NHẬN DIỆN BOT & UNIQUE VIEW ---
            chrome_options.add_argument("--incognito")  # Ẩn danh: không lưu cache, cookie, local storage
            chrome_options.add_argument("--disable-gpu")
            chrome_options.add_argument("--no-sandbox")
            chrome_options.add_argument("--disable-dev-shm-usage")
            
            # Ẩn hoàn toàn dấu hiệu webdriver tự động
            chrome_options.add_argument("--disable-blink-features=AutomationControlled")
            chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
            chrome_options.add_experimental_option("useAutomationExtension", False)
            
            # Cấu hình chặn lưu file rác xuống ổ cứng máy tính
            prefs = {
                "download.default_directory": temp_dl_dir,
                "download.prompt_for_download": False,
                "download.directory_upgrade": True,
                "safebrowsing.enabled": True
            }
            chrome_options.add_experimental_option("prefs", prefs)

            # Chọn ngẫu nhiên User-Agent
            selected_ua = random.choice(USER_AGENTS)
            chrome_options.add_argument(f"user-agent={selected_ua}")
            chrome_options.add_argument("--log-level=3")

            # Xoay vòng Proxy (nếu có)
            if proxies_list and len(proxies_list) > 0:
                proxy = proxies_list[(i - 1) % len(proxies_list)]
                chrome_options.add_argument(f"--proxy-server={proxy}")
                add_log(f"[-] Phiên {i}: Sử dụng Proxy {proxy}")

            service = Service(ChromeDriverManager().install())
            driver = webdriver.Chrome(service=service, options=chrome_options)
            
            with bot_state["lock"]:
                bot_state["current_driver"] = driver

            # Tiêm script vô hiệu hóa cờ navigator.webdriver (Stealth Mode)
            try:
                driver.execute_cdp_cmd(
                    "Page.addScriptToEvaluateOnNewDocument",
                    {
                        "source": """
                            Object.defineProperty(navigator, 'webdriver', {get: () => undefined});
                            window.chrome = { runtime: {} };
                            Object.defineProperty(navigator, 'languages', {get: () => ['en-US', 'en', 'vi']});
                            Object.defineProperty(navigator, 'plugins', {get: () => [1, 2, 3, 4, 5]});
                        """
                    }
                )
            except Exception:
                pass

            driver.set_page_load_timeout(35)

            # Đổi ngẫu nhiên kích thước cửa sổ giả lập thiết bị khác nhau
            w, h = random.choice(VIEWPORT_SIZES)
            driver.set_window_size(w, h)

            start_time = time.time()
            driver.get(url)

            # Chờ trang load ổn định trong 2.5 - 3 giây
            time.sleep(2.5)

            # 1. Kích hoạt hành động bấm nút tải xuống nếu được bật
            if do_download and bot_state["is_running"]:
                simulate_download_action(driver)

            # 2. Kích hoạt hành động gửi bình luận nếu được bật
            if do_comment and bot_state["is_running"]:
                simulate_comment_action(driver, custom_comments)

            view_duration = random.uniform(min_wait, max_wait)

            # Chờ ngắt quãng và giả lập cuộn trang tự nhiên
            slept = 0.0
            while slept < view_duration and bot_state["is_running"]:
                step = min(1.0, view_duration - slept)
                time.sleep(step)
                slept += step

                if do_scroll and bot_state["is_running"] and random.random() < 0.65:
                    try:
                        scroll_y = random.randint(150, 420)
                        driver.execute_script(f"window.scrollBy({{top: {scroll_y}, behavior: 'smooth'}});")
                    except Exception:
                        pass

            if not bot_state["is_running"]:
                break

            elapsed = time.time() - start_time
            with bot_state["lock"]:
                bot_state["success_count"] += 1
            add_log(f"[+] Lượt [{i}/{total_sessions}] -> Hoàn tất phiên ({elapsed:.1f}s)")

        except (WebDriverException, TimeoutException) as e:
            with bot_state["lock"]:
                bot_state["fail_count"] += 1
            err_msg = str(e).splitlines()[0] if str(e).splitlines() else "Lỗi kết nối"
            add_log(f"[!] Lượt [{i}/{total_sessions}] -> Lỗi: {err_msg}")
        except Exception as e:
            with bot_state["lock"]:
                bot_state["fail_count"] += 1
            add_log(f"[!] Lượt [{i}/{total_sessions}] -> Ngoại lệ: {e}")
        finally:
            with bot_state["lock"]:
                bot_state["current_driver"] = None
            if driver:
                try:
                    driver.quit()
                except Exception:
                    pass
            # Dọn dẹp sạch sẽ thư mục tải tạm thời ngay lập tức
            if temp_dl_dir and os.path.exists(temp_dl_dir):
                try:
                    shutil.rmtree(temp_dl_dir, ignore_errors=True)
                except Exception:
                    pass

        # Khoảng nghỉ an toàn (5s - 10s) để tránh bị Itch.io rate-limit quét IP
        if i < total_sessions and bot_state["is_running"]:
            cooldown = random.uniform(5.0, 10.0)
            slept_cd = 0.0
            while slept_cd < cooldown and bot_state["is_running"]:
                time.sleep(0.5)
                slept_cd += 0.5

    with bot_state["lock"]:
        bot_state["is_running"] = False
    add_log(f"[*] Hoàn tất chiến dịch! View thành công: {bot_state['success_count']} | Lượt tải: {bot_state['download_count']} | Bình luận: {bot_state['comment_count']} | Thất bại: {bot_state['fail_count']}")

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/api/status")
def get_status():
    with bot_state["lock"]:
        return jsonify({
            "is_running": bot_state["is_running"],
            "current_view": bot_state["current_view"],
            "total_views": bot_state["total_views"],
            "success_count": bot_state["success_count"],
            "fail_count": bot_state["fail_count"],
            "download_count": bot_state["download_count"],
            "comment_count": bot_state["comment_count"],
            "logs": bot_state["logs"]
        })

@app.route("/api/start", methods=["POST"])
def start_campaign():
    data = request.get_json() or {}
    url = data.get("url", "").strip()
    total_sessions = int(data.get("total_sessions", 10))
    min_wait = float(data.get("min_wait", 8.0))
    max_wait = float(data.get("max_wait", 15.0))
    is_headless = bool(data.get("headless", True))
    do_scroll = bool(data.get("scroll", True))
    do_download = bool(data.get("download", True))
    do_comment = bool(data.get("comment", False))
    raw_comments = data.get("comments", "")
    raw_proxies = data.get("proxies", "")

    custom_comments = []
    if raw_comments:
        for line in raw_comments.splitlines():
            c = line.strip()
            if c:
                custom_comments.append(c)

    proxies_list = []
    if raw_proxies:
        for line in raw_proxies.splitlines():
            p = line.strip()
            if p:
                proxies_list.append(p)

    if not url or url == "https://example.com":
        return jsonify({"success": False, "message": "Vui lòng nhập URL mục tiêu hợp lệ!"}), 400

    if not (url.startswith("http://") or url.startswith("https://")):
        url = "https://" + url

    if bot_state["is_running"]:
        return jsonify({"success": False, "message": "Bot đang chạy một chiến dịch khác!"}), 400

    with bot_state["lock"]:
        bot_state["is_running"] = True
        bot_state["current_view"] = 0
        bot_state["total_views"] = total_sessions
        bot_state["success_count"] = 0
        bot_state["fail_count"] = 0
        bot_state["download_count"] = 0
        bot_state["comment_count"] = 0

    threading.Thread(
        target=bot_worker,
        args=(url, total_sessions, min_wait, max_wait, is_headless, do_scroll, do_download, do_comment, custom_comments, proxies_list),
        daemon=True
    ).start()

    return jsonify({"success": True, "message": "Đã bắt đầu chiến dịch!"})

@app.route("/api/stop", methods=["POST"])
def stop_campaign():
    with bot_state["lock"]:
        bot_state["is_running"] = False
        add_log("[*] Đang gửi tín hiệu dừng, vui lòng đợi đóng phiên hiện tại...")
        if bot_state["current_driver"]:
            try:
                bot_state["current_driver"].quit()
            except Exception:
                pass
            bot_state["current_driver"] = None
    return jsonify({"success": True})

@app.route("/api/clear_logs", methods=["POST"])
def clear_logs():
    with bot_state["lock"]:
        bot_state["logs"] = []
    return jsonify({"success": True})

if __name__ == "__main__":
    PORT = 5050
    print(f"\n=======================================================")
    print(f"🚀 UpView Web Dashboard đang chạy tại: http://127.0.0.1:{PORT}")
    print(f"=======================================================\n")
    
    app.run(host="0.0.0.0", port=PORT, debug=False)
