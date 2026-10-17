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

def run_view_bot(url, total_sessions, min_wait, max_wait, do_download=True, max_retries_per_session=2):
    """
    Chạy vòng lặp giả lập trình duyệt xem trang web kèm cơ chế tự động thử lại khi có sự cố mạng.
    """
    print(f"[*] Mục tiêu: {url}")
    print(f"[*] Tổng số phiên (views) cấu hình: {total_sessions}")
    print(f"[*] Thời gian xem mỗi phiên: {min_wait}s - {max_wait}s\n")
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
                start_time = time.time()
                driver.get(url)

                time.sleep(2.5)

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
