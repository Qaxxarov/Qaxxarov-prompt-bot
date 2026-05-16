"""
Agro AI — Browser Module (v3)
Reliable Chrome launch with DevToolsActivePort fix.
"""

import logging
import os
import shutil
import subprocess
import tempfile
import time
from pathlib import Path
from typing import Optional

from selenium import webdriver
from selenium.common.exceptions import (
    ElementClickInterceptedException,
    NoSuchElementException,
    SessionNotCreatedException,
    TimeoutException,
    WebDriverException,
)
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
from webdriver_manager.chrome import ChromeDriverManager

import config

logger = logging.getLogger("instagram_analyzer.browser")

_MAX_RETRIES = 3
_RETRY_DELAY = 4


# ════════════════════════════════════════════════════════
# PROCESS & LOCK CLEANUP
# ════════════════════════════════════════════════════════

def _kill_all_chrome() -> int:
    """Kill ALL chrome/chromedriver processes. Cross-platform."""
    import platform
    killed = 0
    system = platform.system()

    if system == "Windows":
        for proc_name in ["chrome.exe", "chromedriver.exe", "chromium.exe"]:
            try:
                r = subprocess.run(
                    ["taskkill", "/F", "/IM", proc_name],
                    capture_output=True, text=True, timeout=10,
                )
                if r.returncode == 0:
                    killed += 1
            except Exception:
                pass
    else:
        # Linux / macOS
        for proc_name in ["chrome", "chromedriver", "chromium", "google-chrome"]:
            try:
                r = subprocess.run(
                    ["pkill", "-f", proc_name],
                    capture_output=True, text=True, timeout=10,
                )
                if r.returncode == 0:
                    killed += 1
            except Exception:
                pass

    if killed:
        time.sleep(2)
    return killed


def _remove_locks(user_data_dir: str, profile_dir: str) -> int:
    """Remove all Chrome lock files."""
    removed = 0
    lock_names = ["SingletonLock", "SingletonCookie", "SingletonSocket", "lockfile"]
    dirs_to_check = [
        Path(user_data_dir),
        Path(user_data_dir) / profile_dir,
    ]
    for d in dirs_to_check:
        for lock_name in lock_names:
            lock_path = d / lock_name
            if lock_path.exists():
                try:
                    lock_path.unlink()
                    removed += 1
                    logger.info(f"  🗑 Lock o'chirildi: {lock_path}")
                except Exception as e:
                    logger.warning(f"  Lock o'chirib bo'lmadi: {lock_path}: {e}")
    return removed


def _remove_devtools_port_file(user_data_dir: str, profile_dir: str) -> None:
    """Remove stale DevToolsActivePort file that causes the error."""
    for d in [Path(user_data_dir) / profile_dir, Path(user_data_dir)]:
        port_file = d / "DevToolsActivePort"
        if port_file.exists():
            try:
                port_file.unlink()
                logger.info(f"  🗑 DevToolsActivePort o'chirildi: {port_file}")
            except Exception:
                pass


# ════════════════════════════════════════════════════════
# CHROME OPTIONS BUILDER
# ════════════════════════════════════════════════════════

def _build_options(user_data_dir: str, profile_dir: str, headless: bool) -> Options:
    """Build Chrome options with all stability flags."""
    opts = Options()

    # ── Profile ──
    opts.add_argument(f"--user-data-dir={user_data_dir}")
    opts.add_argument(f"--profile-directory={profile_dir}")

    # ── DevToolsActivePort fix ──
    opts.add_argument("--remote-debugging-port=9222")

    # ── Stability (critical for Windows) ──
    opts.add_argument("--no-sandbox")
    opts.add_argument("--disable-dev-shm-usage")
    opts.add_argument("--disable-gpu")
    opts.add_argument("--disable-software-rasterizer")
    opts.add_argument("--disable-extensions")
    opts.add_argument("--disable-infobars")
    opts.add_argument("--disable-session-crashed-bubble")
    opts.add_argument("--disable-blink-features=AutomationControlled")
    opts.add_argument("--start-maximized")
    opts.add_argument("--no-first-run")
    opts.add_argument("--no-default-browser-check")
    opts.add_argument("--disable-background-networking")
    opts.add_argument("--disable-sync")
    opts.add_argument("--disable-translate")
    opts.add_argument("--disable-notifications")
    opts.add_argument("--disable-popup-blocking")
    opts.add_argument("--disable-crash-reporter")
    opts.add_argument("--disable-breakpad")
    opts.add_argument("--disable-component-update")
    opts.add_argument("--disable-domain-reliability")
    opts.add_argument("--disable-features=TranslateUI")

    if headless:
        opts.add_argument("--headless=new")
        opts.add_argument("--window-size=1366,768")

    # ── Automation detection bypass ──
    opts.add_experimental_option("excludeSwitches", ["enable-automation", "enable-logging"])
    opts.add_experimental_option("useAutomationExtension", False)

    # ── Preferences ──
    opts.add_experimental_option("prefs", {
        "profile.managed_default_content_settings.images": 2,
        "profile.default_content_setting_values.notifications": 2,
        "credentials_enable_service": False,
        "profile.password_manager_enabled": False,
    })

    return opts


# ════════════════════════════════════════════════════════
# DRIVER BUILDER
# ════════════════════════════════════════════════════════

def build_driver(
    user_data_dir: Optional[str] = None,
    profile_dir: Optional[str] = None,
    headless: Optional[bool] = None,
) -> webdriver.Chrome:
    """
    Build Chrome WebDriver with full reliability.

    Strategy:
    1. Kill all stale Chrome/chromedriver processes
    2. Remove lock files + DevToolsActivePort
    3. Try launching with profile (up to 3 attempts)
    4. If all fail → fallback to temp profile
    """
    _udd = user_data_dir or config.CHROME_USER_DATA_DIR
    _pdir = profile_dir or config.CHROME_PROFILE_DIR
    _headless = headless if headless is not None else config.HEADLESS

    logger.info("═" * 50)
    logger.info("  🚀 CHROME LAUNCH")
    logger.info(f"  📁 User Data: {_udd}")
    logger.info(f"  📁 Profile: {_pdir}")
    logger.info(f"  👁 Headless: {_headless}")
    logger.info("═" * 50)

    # ── Step 1: Kill stale processes ──
    killed = _kill_all_chrome()
    if killed:
        logger.info(f"  ✅ {killed} ta stale jarayon to'xtatildi")

    # ── Step 2: Remove locks ──
    removed = _remove_locks(_udd, _pdir)
    _remove_devtools_port_file(_udd, _pdir)
    if removed:
        logger.info(f"  ✅ {removed} ta lock fayl o'chirildi")
    time.sleep(1)

    # ── Step 3: Get chromedriver ──
    try:
        driver_path = ChromeDriverManager().install()
        logger.info(f"  ✅ ChromeDriver: {driver_path}")
    except Exception as e:
        logger.error(f"  ❌ ChromeDriver yuklab bo'lmadi: {e}")
        raise RuntimeError(f"ChromeDriver yuklab bo'lmadi: {e}")

    # ── Step 4: Try profile launch ──
    last_error: Optional[Exception] = None

    for attempt in range(1, _MAX_RETRIES + 1):
        logger.info(f"  🔄 Urinish {attempt}/{_MAX_RETRIES} (profil: {_pdir})")

        try:
            opts = _build_options(_udd, _pdir, _headless)
            service = Service(driver_path)
            service.creation_flags = 0x08000000  # CREATE_NO_WINDOW on Windows

            driver = webdriver.Chrome(service=service, options=opts)

            # Verify it's alive
            _ = driver.current_url
            driver.execute_script(
                "Object.defineProperty(navigator, 'webdriver', {get: () => undefined})"
            )

            logger.info(f"  ✅ Chrome ishga tushdi! (profil: {_pdir})")
            return driver

        except (SessionNotCreatedException, WebDriverException) as e:
            last_error = e
            err_msg = str(e)
            logger.error(f"  ❌ Urinish {attempt} muvaffaqiyatsiz:")
            logger.error(f"     {err_msg[:200]}")

            # Specific fixes based on error
            if "DevToolsActivePort" in err_msg:
                logger.warning("  → DevToolsActivePort muammosi — tozalanmoqda...")
                _kill_all_chrome()
                _remove_devtools_port_file(_udd, _pdir)
                _remove_locks(_udd, _pdir)

            elif "user data directory is already in use" in err_msg.lower():
                logger.warning("  → Profil band — kill qilinmoqda...")
                _kill_all_chrome()
                _remove_locks(_udd, _pdir)

            elif "chrome not reachable" in err_msg.lower() or "cannot connect" in err_msg.lower():
                logger.warning("  → Chrome ulanib bo'lmadi — qayta kill...")
                _kill_all_chrome()

            time.sleep(_RETRY_DELAY)

        except Exception as e:
            last_error = e
            logger.error(f"  ❌ Kutilmagan xato (urinish {attempt}): {e}")
            time.sleep(_RETRY_DELAY)

    # ── Step 5: Fallback to temp profile ──
    logger.warning("  ⚠️ Profil bilan ishga tushmadi — TEMP PROFIL ishlatilmoqda...")

    try:
        temp_dir = tempfile.mkdtemp(prefix="chrome_agro_")
        logger.info(f"  📁 Temp profil: {temp_dir}")

        _kill_all_chrome()
        time.sleep(2)

        opts = _build_options(temp_dir, "Default", _headless)
        service = Service(driver_path)
        service.creation_flags = 0x08000000

        driver = webdriver.Chrome(service=service, options=opts)
        _ = driver.current_url
        driver.execute_script(
            "Object.defineProperty(navigator, 'webdriver', {get: () => undefined})"
        )

        logger.info("  ✅ Chrome TEMP profilda ishga tushdi!")
        logger.warning("  ⚠️ Instagram sessiyasi bo'lmasligi mumkin (temp profil)")
        return driver

    except Exception as e2:
        logger.error(f"  ❌ Temp profil ham ishlamadi: {e2}")
        raise RuntimeError(
            f"Chrome ishga tushmadi (profil ham, temp ham).\n\n"
            f"Profil xatosi: {last_error}\n"
            f"Temp xatosi: {e2}\n\n"
            "Yechim:\n"
            "1. Task Manager → barcha chrome.exe → End Task\n"
            "2. Kompyuterni restart qiling\n"
            "3. Chrome'ni yangilang (chrome://settings/help)\n"
            "4. Qayta urinib ko'ring"
        )


# ════════════════════════════════════════════════════════
# UTILITY FUNCTIONS
# ════════════════════════════════════════════════════════

def human_delay(min_sec: float = None, max_sec: float = None) -> None:
    import random
    lo = min_sec if min_sec is not None else config.DELAY_MIN
    hi = max_sec if max_sec is not None else config.DELAY_MAX
    time.sleep(random.uniform(lo, hi))


def human_type(element, text: str) -> None:
    import random
    for char in text:
        element.send_keys(char)
        time.sleep(random.uniform(0.05, 0.18))


def safe_find(driver, by, value, timeout=10):
    try:
        return WebDriverWait(driver, timeout).until(
            EC.presence_of_element_located((by, value))
        )
    except TimeoutException:
        return None


def safe_click(driver, element) -> bool:
    try:
        element.click()
        return True
    except ElementClickInterceptedException:
        try:
            driver.execute_script("arguments[0].click();", element)
            return True
        except WebDriverException:
            return False


def scroll_down(driver, pixels: int = 800) -> None:
    driver.execute_script(f"window.scrollBy(0, {pixels});")
    human_delay(0.5, 1.2)


def scroll_to_bottom(driver) -> None:
    last = driver.execute_script("return document.body.scrollHeight")
    while True:
        driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        human_delay(1.5, 3.0)
        new = driver.execute_script("return document.body.scrollHeight")
        if new == last:
            break
        last = new


# ════════════════════════════════════════════════════════
# INSTAGRAM BROWSER
# ════════════════════════════════════════════════════════

class InstagramBrowser:
    """
    Instagram browser — reliable Chrome launch with auto-fallback.
    """

    def __init__(self):
        self.driver = build_driver()
        self.wait = WebDriverWait(self.driver, 15)
        self._logged_in = False
        self._is_temp_profile = False

    def login(self) -> bool:
        """Verify Instagram session is active."""
        logger.info(f"🔍 Instagram sessiyasi tekshirilmoqda (profil: {config.CHROME_PROFILE_DIR})...")

        try:
            self.driver.get(config.INSTAGRAM_BASE_URL)
            human_delay(3, 5)
        except WebDriverException as e:
            logger.error(f"❌ Instagram ochib bo'lmadi: {e}")
            return False

        self._dismiss_cookie_popup()

        if self._is_session_active():
            self._logged_in = True
            logger.info("✅ Instagram sessiyasi faol")
            self._dismiss_notifications_popup()
            return True

        logger.error(
            "❌ Instagram sessiyasi topilmadi.\n"
            f"   Profil: {config.CHROME_PROFILE_DIR}\n"
            "   Chrome'da instagram.com ga kiring, keyin Chrome'ni yoping."
        )
        return False

    def _is_session_active(self) -> bool:
        try:
            url = self.driver.current_url
        except WebDriverException:
            return False

        if "accounts/login" in url:
            return False

        for sel in [
            "svg[aria-label='Home']",
            "svg[aria-label='Search']",
            "a[href='/direct/inbox/']",
            "div[role='main']",
            "nav[role='navigation']",
        ]:
            try:
                self.driver.find_element(By.CSS_SELECTOR, sel)
                return True
            except NoSuchElementException:
                continue

        if "instagram.com" in url and "login" not in url:
            return True
        return False

    def _dismiss_cookie_popup(self) -> None:
        try:
            btn = WebDriverWait(self.driver, 5).until(
                EC.element_to_be_clickable((
                    By.XPATH,
                    "//button[contains(text(),'Allow') or contains(text(),'Accept')"
                    " or contains(text(),'Decline') or contains(text(),'OK')]",
                ))
            )
            safe_click(self.driver, btn)
            human_delay(1, 2)
        except TimeoutException:
            pass

    def _dismiss_notifications_popup(self) -> None:
        try:
            btn = WebDriverWait(self.driver, 5).until(
                EC.element_to_be_clickable((
                    By.XPATH,
                    "//button[contains(text(),'Not Now') or contains(text(),'Not now')"
                    " or contains(text(),'Skip')]",
                ))
            )
            safe_click(self.driver, btn)
            human_delay(1, 2)
        except TimeoutException:
            pass

    def open_reels_page(self, username: str = None) -> bool:
        target = (username or config.TARGET_PROFILE).lstrip("@")
        url = f"{config.INSTAGRAM_BASE_URL}/{target}/reels/"
        logger.info(f"📱 Reels sahifasi: {url}")
        try:
            self.driver.get(url)
            human_delay(3, 5)
        except WebDriverException as e:
            logger.error(f"❌ Sahifani ochib bo'lmadi: {e}")
            return False
        try:
            title = self.driver.title
            source = self.driver.page_source[:500]
        except Exception:
            return False
        if "Page Not Found" in title or "Sorry" in source:
            logger.error(f"❌ Profil topilmadi: @{target}")
            return False
        logger.info(f"✅ Reels sahifasi ochildi: @{target}")
        return True

    def close(self) -> None:
        try:
            self.driver.quit()
            logger.info("🔒 Brauzer yopildi")
        except Exception:
            pass

    def force_close(self) -> None:
        self.close()

    def __enter__(self):
        return self

    def __exit__(self, *_):
        self.close()
