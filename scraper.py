"""
╔══════════════════════════════════════════════════════╗
║       Instagram Reels Analyzer — Scraper Module      ║
║       Reels ma'lumotlarini yig'ish                   ║
╚══════════════════════════════════════════════════════╝
"""

import logging
import random
import re
import time
from dataclasses import dataclass, field
from typing import List, Optional

from selenium.common.exceptions import NoSuchElementException, TimeoutException
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait

import config
from browser import InstagramBrowser, human_delay, safe_click, scroll_down

logger = logging.getLogger("instagram_analyzer.scraper")


# ════════════════════════════════════════════════════════
# 📦 DATA MODELS
# ════════════════════════════════════════════════════════

@dataclass
class ReelData:
    """Bitta reel ma'lumotlari."""
    url: str = ""
    shortcode: str = ""
    thumbnail_url: str = ""
    caption: str = ""
    views: int = 0
    likes: int = 0
    comments: int = 0
    shares: int = 0
    plays: int = 0
    duration_sec: int = 0
    posted_at: str = ""
    hashtags: List[str] = field(default_factory=list)
    mentions: List[str] = field(default_factory=list)

    @property
    def engagement_rate(self) -> float:
        """Engagement rate = (likes + comments + shares) / views * 100."""
        if self.views == 0:
            return 0.0
        return round((self.likes + self.comments + self.shares) / self.views * 100, 2)

    def to_dict(self) -> dict:
        return {
            "url": self.url,
            "shortcode": self.shortcode,
            "caption": self.caption[:100] + "..." if len(self.caption) > 100 else self.caption,
            "views": self.views,
            "likes": self.likes,
            "comments": self.comments,
            "shares": self.shares,
            "plays": self.plays,
            "duration_sec": self.duration_sec,
            "posted_at": self.posted_at,
            "engagement_rate": self.engagement_rate,
            "hashtags": ", ".join(self.hashtags),
            "mentions": ", ".join(self.mentions),
        }


@dataclass
class ProfileData:
    """Profil umumiy ma'lumotlari."""
    username: str = ""
    full_name: str = ""
    bio: str = ""
    followers: int = 0
    following: int = 0
    posts_count: int = 0
    is_verified: bool = False
    profile_url: str = ""


# ════════════════════════════════════════════════════════
# 🔢 NUMBER PARSER
# ════════════════════════════════════════════════════════

def parse_count(text: str) -> int:
    """
    Instagram raqamlarini parse qilish.
    "1.2M" → 1200000, "45.3K" → 45300, "1,234" → 1234
    """
    if not text:
        return 0
    text = text.strip().replace(",", "").replace(" ", "")
    try:
        if text.upper().endswith("M"):
            return int(float(text[:-1]) * 1_000_000)
        elif text.upper().endswith("K"):
            return int(float(text[:-1]) * 1_000)
        else:
            # Faqat raqamlarni olish
            digits = re.sub(r"[^\d]", "", text)
            return int(digits) if digits else 0
    except (ValueError, IndexError):
        return 0


def extract_hashtags(text: str) -> List[str]:
    """Matndan hashtaglarni ajratib olish."""
    return re.findall(r"#(\w+)", text)


def extract_mentions(text: str) -> List[str]:
    """Matndan mentionlarni ajratib olish."""
    return re.findall(r"@(\w+)", text)


# ════════════════════════════════════════════════════════
# 🕷️ SCRAPER
# ════════════════════════════════════════════════════════

class ReelsScraper:
    """
    Instagram Reels ma'lumotlarini yig'uvchi klass.
    """

    # CSS selectors (Instagram tez-tez o'zgartiradi — fallback'lar bor)
    SELECTORS = {
        # Reels grid thumbnails
        "reel_links": [
            "a[href*='/reel/']",
            "div[class*='_aagw'] a",
        ],
        # Profile stats
        "followers": [
            "a[href*='/followers/'] span",
            "li:nth-child(2) span span",
        ],
        "following": [
            "a[href*='/following/'] span",
            "li:nth-child(3) span span",
        ],
        "posts_count": [
            "li:nth-child(1) span span",
        ],
        "full_name": [
            "h2._aacl",
            "span._aacl._aaco._aacu._aacx._aad7._aade",
            "h1",
        ],
        "bio": [
            "div._aacl._aaco._aacu._aacx._aad7._aade",
            "span._aacl._aaco._aacu._aacx._aad7._aade",
        ],
        # Reel detail page
        "views_count": [
            "span[class*='_aacl'] span",
            "div[class*='_ae2s'] span",
            "span.html-span",
        ],
        "likes_count": [
            "section span span",
            "div[class*='_ae2s'] span",
        ],
        "caption_text": [
            "div._a9zs h1",
            "div._a9zs span",
            "div[class*='_a9zs']",
        ],
        "posted_time": [
            "time[datetime]",
            "a time",
        ],
    }

    def __init__(self, browser: InstagramBrowser):
        self.browser = browser
        self.driver = browser.driver
        self.wait = WebDriverWait(self.driver, 10)

    # ─────────────────────────────────────────────────────
    # PROFILE
    # ─────────────────────────────────────────────────────

    def scrape_profile(self, username: str = None) -> ProfileData:
        """Profil asosiy ma'lumotlarini yig'ish."""
        target = (username or config.TARGET_PROFILE).lstrip("@")
        url = f"{config.INSTAGRAM_BASE_URL}/{target}/"

        logger.info(f"👤 Profil ma'lumotlari yig'ilmoqda: @{target}")
        self.driver.get(url)
        human_delay(2, 4)

        profile = ProfileData(
            username=target,
            profile_url=url,
        )

        # Full name
        profile.full_name = self._try_selectors_text(self.SELECTORS["full_name"])

        # Bio
        profile.bio = self._try_selectors_text(self.SELECTORS["bio"])

        # Stats — Instagram'da meta tag'lardan ham olish mumkin
        profile.followers = self._scrape_followers()
        profile.following = self._scrape_following()
        profile.posts_count = self._scrape_posts_count()

        # Verified badge
        try:
            self.driver.find_element(By.CSS_SELECTOR, "svg[aria-label='Verified']")
            profile.is_verified = True
        except NoSuchElementException:
            profile.is_verified = False

        logger.info(
            f"✅ Profil: {profile.full_name} | "
            f"Followers: {profile.followers:,} | "
            f"Posts: {profile.posts_count}"
        )
        return profile

    def _scrape_followers(self) -> int:
        """Followers sonini olish."""
        # Meta description'dan ham urinish
        try:
            meta = self.driver.find_element(
                By.CSS_SELECTOR, "meta[name='description']"
            )
            content = meta.get_attribute("content") or ""
            # "1.2M Followers, 500 Following, 150 Posts"
            match = re.search(r"([\d,.]+[KMB]?)\s+Followers", content, re.IGNORECASE)
            if match:
                return parse_count(match.group(1))
        except NoSuchElementException:
            pass

        text = self._try_selectors_text(self.SELECTORS["followers"])
        return parse_count(text)

    def _scrape_following(self) -> int:
        """Following sonini olish."""
        try:
            meta = self.driver.find_element(
                By.CSS_SELECTOR, "meta[name='description']"
            )
            content = meta.get_attribute("content") or ""
            match = re.search(r"([\d,.]+[KMB]?)\s+Following", content, re.IGNORECASE)
            if match:
                return parse_count(match.group(1))
        except NoSuchElementException:
            pass

        text = self._try_selectors_text(self.SELECTORS["following"])
        return parse_count(text)

    def _scrape_posts_count(self) -> int:
        """Posts sonini olish."""
        try:
            meta = self.driver.find_element(
                By.CSS_SELECTOR, "meta[name='description']"
            )
            content = meta.get_attribute("content") or ""
            match = re.search(r"([\d,.]+[KMB]?)\s+Posts", content, re.IGNORECASE)
            if match:
                return parse_count(match.group(1))
        except NoSuchElementException:
            pass

        text = self._try_selectors_text(self.SELECTORS["posts_count"])
        return parse_count(text)

    # ─────────────────────────────────────────────────────
    # REELS LIST
    # ─────────────────────────────────────────────────────

    def collect_reel_urls(self, max_reels: int = None) -> List[str]:
        """
        Reels sahifasidan barcha reel URL larini yig'ish.
        Scroll qilib ko'proq yuklaydi.
        """
        limit = max_reels or config.MAX_REELS
        logger.info(f"🎬 Reel URL'lari yig'ilmoqda (max: {limit})...")

        # Reels sahifasiga o'tish
        if not self.browser.open_reels_page():
            return []

        human_delay(2, 3)

        urls = set()
        scroll_attempts = 0
        max_scroll_attempts = 15

        while len(urls) < limit and scroll_attempts < max_scroll_attempts:
            # Sahifadagi barcha reel linklar
            links = self._find_reel_links()
            new_count = 0
            for link in links:
                href = link.get_attribute("href") or ""
                if "/reel/" in href and href not in urls:
                    urls.add(href)
                    new_count += 1
                    if len(urls) >= limit:
                        break

            logger.info(f"  📊 Topilgan: {len(urls)} ta reel (+{new_count} yangi)")

            if new_count == 0:
                scroll_attempts += 1
            else:
                scroll_attempts = 0

            if len(urls) < limit:
                scroll_down(self.driver, random.randint(600, 1000))

        result = list(urls)[:limit]
        logger.info(f"✅ Jami {len(result)} ta reel URL yig'ildi")
        return result

    def _find_reel_links(self):
        """Reel linklar elementlarini topish."""
        for selector in self.SELECTORS["reel_links"]:
            try:
                elements = self.driver.find_elements(By.CSS_SELECTOR, selector)
                if elements:
                    return elements
            except Exception:
                continue
        return []

    # ─────────────────────────────────────────────────────
    # REEL DETAIL
    # ─────────────────────────────────────────────────────

    def scrape_reel(self, url: str) -> Optional[ReelData]:
        """
        Bitta reel sahifasini ochib ma'lumot yig'ish.
        """
        logger.info(f"  🎥 Reel tahlil: {url}")
        self.driver.get(url)
        human_delay(2, 4)

        reel = ReelData(url=url)

        # Shortcode URL'dan
        match = re.search(r"/reel/([A-Za-z0-9_-]+)/", url)
        if match:
            reel.shortcode = match.group(1)

        # Caption
        reel.caption = self._scrape_caption()
        reel.hashtags = extract_hashtags(reel.caption)
        reel.mentions = extract_mentions(reel.caption)

        # Views — eng muhim metrika
        reel.views = self._scrape_views()

        # Likes
        reel.likes = self._scrape_likes()

        # Comments
        reel.comments = self._scrape_comments()

        # Posted time
        reel.posted_at = self._scrape_posted_time()

        # Thumbnail
        reel.thumbnail_url = self._scrape_thumbnail()

        logger.info(
            f"    👁 Views: {reel.views:,} | "
            f"❤️ Likes: {reel.likes:,} | "
            f"💬 Comments: {reel.comments:,} | "
            f"📈 ER: {reel.engagement_rate}%"
        )
        return reel

    def _scrape_caption(self) -> str:
        """Caption matnini olish."""
        selectors = [
            "div._a9zs h1",
            "div._a9zs span",
            "div[class*='_a9zs'] span",
            "article div[class*='_a9zs']",
            "h1._aacl",
        ]
        for sel in selectors:
            try:
                el = self.driver.find_element(By.CSS_SELECTOR, sel)
                text = el.text.strip()
                if text:
                    return text
            except NoSuchElementException:
                continue
        return ""

    def _scrape_views(self) -> int:
        """Ko'rishlar sonini olish."""
        # Meta tag'dan urinish (eng ishonchli)
        try:
            meta = self.driver.find_element(
                By.CSS_SELECTOR, "meta[property='og:video:duration']"
            )
        except NoSuchElementException:
            pass

        # Views text selectors
        view_selectors = [
            "span.html-span.xdj266r",
            "div._aacl._aaco._aacu._aacx._aad7._aade span",
            "span[class*='_aacl']",
            "div[class*='_ae2s'] span",
        ]
        for sel in view_selectors:
            try:
                elements = self.driver.find_elements(By.CSS_SELECTOR, sel)
                for el in elements:
                    text = el.text.strip()
                    count = parse_count(text)
                    if count > 100:  # Mantiqiy minimum
                        return count
            except Exception:
                continue

        # "X plays" yoki "X views" matnini qidirish
        try:
            page_text = self.driver.find_element(By.TAG_NAME, "body").text
            patterns = [
                r"([\d,.]+[KMB]?)\s+(?:plays|views|ko'rishlar)",
                r"([\d,.]+[KMB]?)\s+plays",
            ]
            for pattern in patterns:
                match = re.search(pattern, page_text, re.IGNORECASE)
                if match:
                    return parse_count(match.group(1))
        except Exception:
            pass

        return 0

    def _scrape_likes(self) -> int:
        """Likes sonini olish."""
        like_selectors = [
            "section span span",
            "div[class*='_ae2s'] span",
            "button[type='button'] span span",
        ]
        for sel in like_selectors:
            try:
                elements = self.driver.find_elements(By.CSS_SELECTOR, sel)
                for el in elements:
                    text = el.text.strip()
                    count = parse_count(text)
                    if 0 < count < 10_000_000:
                        return count
            except Exception:
                continue
        return 0

    def _scrape_comments(self) -> int:
        """Comments sonini olish."""
        try:
            page_text = self.driver.find_element(By.TAG_NAME, "body").text
            match = re.search(
                r"([\d,.]+[KMB]?)\s+(?:comments|izohlar)",
                page_text,
                re.IGNORECASE,
            )
            if match:
                return parse_count(match.group(1))
        except Exception:
            pass
        return 0

    def _scrape_posted_time(self) -> str:
        """Post vaqtini olish."""
        try:
            time_el = self.driver.find_element(By.CSS_SELECTOR, "time[datetime]")
            return time_el.get_attribute("datetime") or time_el.text
        except NoSuchElementException:
            pass
        return ""

    def _scrape_thumbnail(self) -> str:
        """Thumbnail URL olish."""
        try:
            meta = self.driver.find_element(
                By.CSS_SELECTOR, "meta[property='og:image']"
            )
            return meta.get_attribute("content") or ""
        except NoSuchElementException:
            return ""

    # ─────────────────────────────────────────────────────
    # HELPERS
    # ─────────────────────────────────────────────────────

    def _try_selectors_text(self, selectors: List[str]) -> str:
        """Bir nechta selector'dan birinchi topilgan matnni qaytarish."""
        for sel in selectors:
            try:
                el = self.driver.find_element(By.CSS_SELECTOR, sel)
                text = el.text.strip()
                if text:
                    return text
            except NoSuchElementException:
                continue
        return ""

    # ─────────────────────────────────────────────────────
    # FULL SCRAPE
    # ─────────────────────────────────────────────────────

    def scrape_all_reels(self, username: str = None) -> tuple[ProfileData, List[ReelData]]:
        """
        To'liq scraping: profil + barcha reels.
        Returns: (profile, reels_list)
        """
        target = (username or config.TARGET_PROFILE).lstrip("@")

        # 1. Profil ma'lumotlari
        profile = self.scrape_profile(target)

        # 2. Reel URL'larini yig'ish
        reel_urls = self.collect_reel_urls()

        if not reel_urls:
            logger.warning("⚠️ Hech qanday reel topilmadi")
            return profile, []

        # 3. Har bir reelni tahlil qilish
        reels = []
        for i, url in enumerate(reel_urls, 1):
            logger.info(f"📹 [{i}/{len(reel_urls)}] Reel tahlil qilinmoqda...")
            try:
                reel = self.scrape_reel(url)
                if reel:
                    reels.append(reel)
            except Exception as e:
                logger.error(f"❌ Reel xatosi ({url}): {e}")
            human_delay(config.DELAY_MIN, config.DELAY_MAX)

        logger.info(f"✅ Jami {len(reels)} ta reel tahlil qilindi")
        return profile, reels
