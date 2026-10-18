#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Tên tool: Selenium Automated View Bot
Mô tả: Giả lập trình duyệt Chrome để truy cập website, đọc trang và tính view chuẩn xác.
"""

import os
import sys
import time
import random
import warnings
import tempfile
import shutil

# Tắt cảnh báo thư viện hệ thống (như urllib3 LibreSSL trên macOS)
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
    print("[-] Thiếu thư viện. Hãy chạy lệnh cài đặt: pip install selenium webdriver-manager")
    sys.exit(1)

# Danh sách User-Agent phổ biến để giả lập đa dạng thiết bị và trình duyệt người dùng thật
USER_AGENTS = [
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/128.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/128.0.0.0 Safari/537.36",
    "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/128.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.5 Safari/605.1.15",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:129.0) Gecko/20100101 Firefox/129.0"
]

def simulate_reading(driver, duration):
    """
    Giả lập hành vi người dùng cuộn trang và đọc nội dung nhẹ nhàng.
    """
    start = time.time()
    while time.time() - start < duration:
        # Cuộn ngẫu nhiên một khoảng ngắn
        scroll_px = random.randint(150, 450)
        driver.execute_script(f"window.scrollBy({{top: {scroll_px}, behavior: 'smooth'}});")
        time.sleep(random.uniform(1.0, 2.5))
        
        # Thỉnh thoảng cuộn ngược lại một chút (hành vi đọc lại)
        if random.random() < 0.3:
            driver.execute_script("window.scrollBy({top: -100, behavior: 'smooth'});")
            time.sleep(random.uniform(0.8, 1.5))

def simulate_download_action(driver):
    """
    Tự động tìm và click nút download trên trang Itch.io.
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
            print("[*] Đã tìm thấy nút Download, đang tiến hành click...")
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
                        print("[*] Phát hiện trang xác nhận tải, chuyển tiếp đến tệp...")
                        dl.click()
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
                        print("[*] Kích hoạt tải tệp game...")
                        fd.click()
                        time.sleep(random.uniform(2.5, 4.0))
                        break
            except Exception:
                pass

            print("[📥] Đã kích hoạt yêu cầu tải file thành công lên server Itch.io!")
            return True
        else:
            return False
    except Exception as e:
        print(f"[!] Lỗi khi click nút Download: {str(e).splitlines()[0]}")
        return False

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

def inject_itchio_cookies(driver, cookie_raw):
    """
    Nạp cookie phiên đăng nhập Itch.io vào trình duyệt trước khi mở trang game.
    """
    if not cookie_raw or not cookie_raw.strip():
        return False
        
    try:
        raw = cookie_raw.strip()
        driver.get("https://itch.io/robots.txt")
        time.sleep(1.0)
        
        if raw.startswith("[") and raw.endswith("]"):
            import json
            cookie_list = json.loads(raw)
            count = 0
            for c in cookie_list:
                name = c.get("name")
                val = c.get("value")
                if name and val:
                    driver.add_cookie({
                        "name": name,
                        "value": val,
                        "domain": ".itch.io",
                        "path": "/",
                        "secure": True
                    })
                    count += 1
            print(f"[🍪] Đã nạp {count} Cookie JSON xác thực tài khoản Itch.io!")
            return True

        if "=" in raw:
            parts = raw.split(";")
            injected = 0
            for part in parts:
                part = part.strip()
                if "=" in part:
                    k, v = part.split("=", 1)
                    k = k.strip()
                    v = v.strip().strip('"')
                    if k:
                        driver.add_cookie({
                            "name": k,
                            "value": v,
                            "domain": ".itch.io",
                            "path": "/",
                            "secure": True
                        })
                        injected += 1
            if injected > 0:
                print(f"[🍪] Đã nạp thành công {injected} Cookie xác thực Itch.io!")
                return True

        driver.add_cookie({
            "name": "itchio",
            "value": raw,
            "domain": ".itch.io",
            "path": "/",
            "secure": True
        })
        print("[🍪] Đã nạp cookie 'itchio' phiên đăng nhập thành công!")
        return True
    except Exception as e:
        print(f"[!] Lỗi khi nạp Cookie: {e}")
        return False

def simulate_comment_action(driver, custom_comments=None, base_url=None):
    """
    Hàm tự động định vị khung bình luận 'Write your comment...', click kích hoạt,
    nhập nội dung ngẫu nhiên và bấm gửi trên Itch.io mà không bao giờ bị lỗi 'stale element reference'.
    """
    try:
        # Nếu đang bị chuyển hướng sang trang /download/ hoặc trang khác, quay lại trang game chính
        if base_url and ("/download" in driver.current_url or "/file/" in driver.current_url):
            print("[*] Đang điều hướng lại trang chính để bình luận...")
            driver.get(base_url)
            time.sleep(2.5)

        # Đóng popup / lightbox quyên góp nếu đang mở che khuất trang
        try:
            close_btns = driver.find_elements(By.CSS_SELECTOR, ".close_lightbox_btn, .lightbox_close, a.close, button.close, .close_button")
            for cb in close_btns:
                if cb.is_displayed():
                    cb.click()
                    time.sleep(0.5)
                    break
        except Exception:
            pass

        # Cuộn trang đến đúng khu vực #comments hoặc widget bình luận
        try:
            driver.execute_script("""
                var el = document.getElementById('comments') || 
                         document.querySelector('.game_comments_widget') || 
                         document.querySelector('.community_topic_posts_widget') ||
                         document.querySelector('[placeholder*="comment" i]') ||
                         document.querySelector('textarea');
                if (el) {
                    el.scrollIntoView({behavior: 'smooth', block: 'center'});
                } else {
                    window.scrollTo({top: document.body.scrollHeight, behavior: 'smooth'});
                }
            """)
        except Exception:
            pass
        time.sleep(2.0)

        # Kiểm tra xem có yêu cầu đăng nhập không (nếu cookie không hợp lệ hoặc hết hạn)
        try:
            login_req = driver.find_elements(By.CSS_SELECTOR, ".game_comments_widget .form_placeholder a[href*='login'], #comments ~ .form_placeholder a[href*='login'], a[@data-register_action='comment']")
            for lr in login_req:
                if lr.is_displayed():
                    print("[⚠️] Itch.io yêu cầu đăng nhập để bình luận! Hãy chắc chắn Cookie 'itchio' đã nạp là tài khoản hợp lệ.")
                    break
        except Exception:
            pass

        # 1. KÍCH HOẠT / MỞ KHUNG NHẬP BÌNH LUẬN (Click placeholder nếu có)
        # Sử dụng JavaScript trực tiếp để click placeholder, tránh lưu tham chiếu Selenium có thể bị stale
        driver.execute_script("""
            var selectors = [
                "*[placeholder*='Write your comment' i]",
                ".game_comments_widget .form_placeholder button",
                ".game_comments_widget .form_placeholder",
                ".form_placeholder",
                "*[placeholder*='comment' i]",
                "textarea[name='body']",
                ".comment_form textarea",
                ".toggle_comment_btn",
                ".btn_add_comment"
            ];
            for (var i = 0; i < selectors.length; i++) {
                var el = document.querySelector(selectors[i]);
                if (el && (el.offsetWidth > 0 || el.offsetHeight > 0 || window.getComputedStyle(el).display !== 'none')) {
                    el.scrollIntoView({behavior: 'smooth', block: 'center'});
                    el.click();
                    return true;
                }
            }
            return false;
        """)
        time.sleep(1.8) # Chờ Itch.io thay thế DOM placeholder thành <form class="comment_form">

        # 2. CHUẨN BỊ NỘI DUNG BÌNH LUẬN
        comments_pool = custom_comments if (custom_comments and len(custom_comments) > 0) else SAMPLE_COMMENTS
        comment_text = random.choice(comments_pool)
        display_txt = comment_text[:40] + "..." if len(comment_text) > 40 else comment_text

        # 3. NHẬP NỘI DUNG VÀO TEXTAREA
        # Phương pháp 1: Pure JavaScript Injection (Tuyệt đối không bao giờ bị Stale Element Reference)
        typed_via_js = driver.execute_script("""
            var text = arguments[0];
            var selectors = [
                "textarea[name='body']",
                ".comment_form textarea",
                "form.comment_form textarea",
                "#comments ~ form textarea",
                ".game_comments_widget textarea",
                "#comment_body",
                "form textarea",
                "textarea",
                "[contenteditable='true']",
                "input[name='body']"
            ];
            for (var i = 0; i < selectors.length; i++) {
                var el = document.querySelector(selectors[i]);
                if (el && (el.offsetWidth > 0 || el.offsetHeight > 0 || window.getComputedStyle(el).display !== 'none')) {
                    el.scrollIntoView({behavior: 'smooth', block: 'center'});
                    el.focus();
                    if (el.tagName.toLowerCase() === 'textarea' || el.tagName.toLowerCase() === 'input') {
                        el.value = text;
                    } else {
                        el.innerText = text;
                    }
                    el.dispatchEvent(new Event('input', {bubbles: true}));
                    el.dispatchEvent(new Event('change', {bubbles: true}));
                    return true;
                }
            }
            return false;
        """, comment_text)

        # Phương pháp 2: Nếu JS chưa tìm thấy ô, thử tìm fresh elements từ DOM qua Selenium
        if not typed_via_js:
            try:
                fresh_boxes = driver.find_elements(By.CSS_SELECTOR, "textarea[name='body'], .comment_form textarea, form textarea, textarea")
                for fb in fresh_boxes:
                    try:
                        if fb.is_displayed():
                            fb.clear()
                            fb.send_keys(comment_text)
                            typed_via_js = True
                            break
                    except Exception:
                        continue
            except Exception:
                pass

        if not typed_via_js:
            # Kiểm tra xem có phải do chưa đăng nhập không
            login_req = driver.find_elements(By.XPATH, "//p[contains(@class, 'form_placeholder')]//a[contains(@href, 'login') or contains(text(), 'Log in')] | //a[@data-register_action='comment']")
            if login_req:
                print("[⚠️] Itch.io BẮT BUỘC ĐĂNG NHẬP để comment! Hãy cung cấp Cookie tài khoản ('itchio').")
            else:
                print("[-] Không tìm thấy ô nhập bình luận (Trang có thể đã khóa tính năng bình luận).")
            return False

        print(f"[*] Đã nhập bình luận: \"{display_txt}\"")
        time.sleep(1.5)

        # 4. BẤM NÚT GỬI (SUBMIT)
        # Sử dụng JS để click nút Submit trực tiếp từ DOM mới nhất, an toàn và chống Stale Element
        submitted = driver.execute_script("""
            var selectors = [
                "form.comment_form button[type='submit']",
                "form.comment_form input[type='submit']",
                "form.comment_form .buttons button",
                "button.post_comment_btn",
                ".post_comment_btn",
                "input[type='submit'][value*='Post' i]",
                "input[type='submit'][value*='Comment' i]",
                "form.comment_form button",
                "#comments ~ form button[type='submit']",
                ".game_comments_widget button[type='submit']",
                "button[type='submit']",
                "input[type='submit']"
            ];
            for (var i = 0; i < selectors.length; i++) {
                var btn = document.querySelector(selectors[i]);
                if (btn && (btn.offsetWidth > 0 || btn.offsetHeight > 0)) {
                    btn.scrollIntoView({behavior: 'smooth', block: 'center'});
                    btn.click();
                    return true;
                }
            }
            // Fallback tìm button theo text
            var allBtns = document.querySelectorAll('button, input[type=\"submit\"], a.button');
            for (var j = 0; j < allBtns.length; j++) {
                var val = (allBtns[j].innerText || allBtns[j].value || '').toLowerCase();
                if (val.includes('post comment') || (val.includes('post') && val.includes('comment'))) {
                    allBtns[j].scrollIntoView({behavior: 'smooth', block: 'center'});
                    allBtns[j].click();
                    return true;
                }
            }
            return false;
        """)

        # Fallback bằng Selenium nếu JS chưa bấm được
        if not submitted:
            try:
                btns = driver.find_elements(By.CSS_SELECTOR, "form.comment_form button[type='submit'], button[type='submit'], input[type='submit']")
                for btn in btns:
                    try:
                        if btn.is_displayed():
                            btn.click()
                            submitted = True
                            break
                    except Exception:
                        continue
            except Exception:
                pass

        if not submitted:
            print("[-] Không tìm thấy nút gửi bình luận (Submit).")
            return False

        time.sleep(3.5)

        # Kiểm tra thông báo lỗi từ Itch.io (nếu có, ví dụ spam filter hoặc form error)
        try:
            err_elements = driver.find_elements(By.CSS_SELECTOR, ".form_errors, .flash_message.error")
            for err_el in err_elements:
                if err_el.is_displayed() and err_el.text.strip():
                    print(f"[!] Lỗi từ Itch.io khi gửi comment: {err_el.text.strip()}")
                    return False
        except Exception:
            pass

        print(f"[💬] Đã gửi bình luận thành công: \"{display_txt}\"")
        return True

    except Exception as e:
        err = str(e).splitlines()[0] if str(e).splitlines() else "Lỗi không xác định"
        print(f"[!] Không thể gửi bình luận: {err}")
        return False

def create_driver(headless=True, proxy=None, temp_dl_dir=None):
    """
    Khởi tạo phiên Chrome với các cờ tối ưu hóa tốc độ, ẩn danh và chống phát hiện bot cho Itch.io.
    """
    chrome_options = Options()
    if headless:
        chrome_options.add_argument("--headless=new")
    chrome_options.add_argument("--incognito")  # Bật chế độ ẩn danh: không lưu cache, cookie, local storage
    chrome_options.add_argument("--disable-gpu")
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    chrome_options.add_argument("--disable-blink-features=AutomationControlled")
    chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
    chrome_options.add_experimental_option("useAutomationExtension", False)

    # Chặn lưu file rác xuống máy
    if temp_dl_dir:
        prefs = {
            "download.default_directory": temp_dl_dir,
            "download.prompt_for_download": False,
            "download.directory_upgrade": True,
            "safebrowsing.enabled": True
        }
        chrome_options.add_experimental_option("prefs", prefs)
    
    chrome_options.add_argument(f"user-agent={random.choice(USER_AGENTS)}")
    chrome_options.add_argument("--log-level=3")

    if proxy:
        chrome_options.add_argument(f"--proxy-server={proxy}")

    service = Service(ChromeDriverManager().install())
    driver = webdriver.Chrome(service=service, options=chrome_options)

    # Tiêm script vô hiệu hóa cờ navigator.webdriver (Stealth Mode)
    try:
        driver.execute_cdp_cmd(
            "Page.addScriptToEvaluateOnNewDocument",
            {
                "source": """
                    Object.defineProperty(navigator, 'webdriver', {get: () => undefined});
                    window.chrome = { runtime: {} };
                    Object.defineProperty(navigator, 'languages', {get: () => ['en-US', 'en', 'vi']});
                """
            }
        )
    except Exception:
        pass

    driver.set_page_load_timeout(35)
    width = random.choice([1366, 1440, 1920, 1280, 1536])
    height = random.choice([768, 900, 1080, 800, 864])
    driver.set_window_size(width, height)
    return driver

def run_view_bot(url, total_sessions, min_wait, max_wait, do_download=True, do_comment=False, custom_comments=None, cookie=None, max_retries_per_session=2):
    """
    Chạy vòng lặp giả lập trình duyệt xem trang web kèm cơ chế tự động thử lại khi có sự cố mạng.
    """
    print(f"[*] Mục tiêu: {url}")
    print(f"[*] Tổng số phiên (views) cấu hình: {total_sessions}")
    print(f"[*] Thời gian xem mỗi phiên: {min_wait}s - {max_wait}s")
    print(f"[*] Chế độ: Download={'Bật' if do_download else 'Tắt'} | Comment={'Bật' if do_comment else 'Tắt'}\n")
    print("-" * 60)

    success_count = 0
    fail_count = 0

    for i in range(1, total_sessions + 1):
        session_success = False
        attempt = 0

        while attempt <= max_retries_per_session and not session_success:
            driver = None
            temp_dl_dir = None
            attempt += 1
            if attempt > 1:
                print(f"[-] [Thử lại {attempt - 1}/{max_retries_per_session}] Phiên {i}...")

            try:
                temp_dl_dir = tempfile.mkdtemp(prefix="itch_cli_dl_")
                driver = create_driver(headless=True, temp_dl_dir=temp_dl_dir)
                
                if do_comment and cookie:
                    inject_itchio_cookies(driver, cookie)

                start_time = time.time()
                driver.get(url)

                time.sleep(2.5)

                if do_comment:
                    simulate_comment_action(driver, custom_comments, base_url=url)

                if do_download:
                    simulate_download_action(driver)

                # Thời gian chờ ngẫu nhiên giống người thật (để load script/analytics)
                view_duration = random.uniform(min_wait, max_wait)
                
                # Giả lập cuộn trang đọc bài
                simulate_reading(driver, view_duration)

                elapsed = time.time() - start_time
                success_count += 1
                session_success = True
                print(f"[+] View [{i}/{total_sessions}] -> Hoàn tất (Thời gian trên trang: {elapsed:.2f}s)")

            except (WebDriverException, TimeoutException) as e:
                err_msg = str(e).split("\n")[0]
                if attempt > max_retries_per_session:
                    fail_count += 1
                    print(f"[!] View [{i}/{total_sessions}] -> Lỗi kết nối sau {max_retries_per_session} lần thử lại: {err_msg}")
                else:
                    print(f"[!] Gặp sự cố kết nối: {err_msg}. Đang chuẩn bị thử lại...")
                    time.sleep(2)
            except Exception as e:
                fail_count += 1
                print(f"[!] View [{i}/{total_sessions}] -> Lỗi không xác định: {e}")
                break
            finally:
                if driver:
                    try:
                        driver.quit()
                    except Exception:
                        pass
                if temp_dl_dir and os.path.exists(temp_dl_dir):
                    try:
                        shutil.rmtree(temp_dl_dir, ignore_errors=True)
                    except Exception:
                        pass

        # Khoảng nghỉ giữa các phiên (5 đến 10 giây) để tránh bị Itch.io rate-limit quét IP
        if i < total_sessions:
            cooldown = random.uniform(5.0, 10.0)
            time.sleep(cooldown)

    print("-" * 60)
    print(f"[*] Hoàn thành toàn bộ chiến dịch.")
    print(f"[*] Thành công: {success_count} | Thất bại: {fail_count}")

if __name__ == "__main__":
    # --- CẤU HÌNH THÔNG SỐ MẶC ĐỊNH ---
    TARGET_URL = "https://example.com"  # <--- Thay link website của boss man vào đây
    TOTAL_SESSIONS = 5                  # <--- Số lượng view cần chạy
    MIN_WAIT_SECONDS = 5.0              # <--- Thời gian ở lại trang tối thiểu (giây)
    MAX_WAIT_SECONDS = 12.0             # <--- Thời gian ở lại trang tối đa (giây)
    # ----------------------------------

    # Cho phép truyền tham số từ dòng lệnh: python view_bot.py [url] [sessions] [min_wait] [max_wait]
    if len(sys.argv) > 1 and not sys.argv[1].startswith("-"):
        TARGET_URL = sys.argv[1]
    if len(sys.argv) > 2:
        try:
            TOTAL_SESSIONS = int(sys.argv[2])
        except ValueError:
            pass
    if len(sys.argv) > 3:
        try:
            MIN_WAIT_SECONDS = float(sys.argv[3])
        except ValueError:
            pass
    if len(sys.argv) > 4:
        try:
            MAX_WAIT_SECONDS = float(sys.argv[4])
        except ValueError:
            pass

    if TARGET_URL == "https://example.com":
        print("[!] Cảnh báo: Vui lòng cập nhật TARGET_URL chính xác trước khi chạy.")
        print("[*] Cách 1: Mở file view_bot.py sửa biến TARGET_URL.")
        print("[*] Cách 2: Chạy trực tiếp kèm URL: python view_bot.py https://my-website.com 5 5 12")
        sys.exit(1)

    run_view_bot(TARGET_URL, TOTAL_SESSIONS, MIN_WAIT_SECONDS, MAX_WAIT_SECONDS)
