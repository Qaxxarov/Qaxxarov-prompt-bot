"""
Agro AI — Production Scraping Pipeline
Wraps browser + scraper with retry, recovery, health tracking, and memory integration.
"""

import logging
import os
import sys
import time
import traceback
from dataclasses import dataclass, field
from pathlib import Path
from typing import Callable, Dict, List, Optional, Tuple

# Ensure root is in path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent))

from app.accounts import Account, accounts
from app.memory import memory
from app.settings import CHROME_PROFILE_DIR, CHROME_USER_DATA_DIR, MAX_REELS, TARGET_PROFILE

logger = logging.getLogger("agro_ai.scraper.pipeline")


@dataclass
class ScrapeResult:
    """Scraping natijasi."""
    success: bool = False
    profile: object = None       # ProfileData
    reels: List = field(default_factory=list)
    stats: Optional[Dict] = None
    ideas: List = field(default_factory=list)
    recommendations: List[str] = field(default_factory=list)
    error: str = ""
    duration_sec: float = 0
    attempt_count: int = 0
    used_temp_profile: bool = False


class ScrapingPipeline:
    """
    Production-grade Instagram scraping pipeline.
    
    Features:
    - 3-attempt retry with progressive recovery
    - Automatic Chrome process cleanup between attempts
    - Temp profile fallback on persistent failure
    - Health tracking integration (watchdog)
    - Memory integration (saves viral hooks automatically)
    - Detailed error diagnostics
    """

    MAX_ATTEMPTS = 3
    ATTEMPT_DELAYS = [0, 5, 10]  # Seconds between attempts

    def __init__(self, account: Optional[Account] = None):
        self.account = account or accounts.active
        self._on_status: Optional[Callable] = None

    def set_status_callback(self, callback: Callable[[str], None]) -> None:
        """Set a callback for status updates (used by Telegram handler)."""
        self._on_status = callback

    def _status(self, msg: str) -> None:
        """Emit status update."""
        logger.info(msg)
        if self._on_status:
            try:
                self._on_status(msg)
            except Exception:
                pass

    def run(self, target: Optional[str] = None, max_reels: Optional[int] = None) -> ScrapeResult:
        """
        Execute full scraping pipeline (SYNCHRONOUS — call from thread pool).
        
        Returns ScrapeResult with all data or error details.
        """
        target_username = target or self.account.username or TARGET_PROFILE
        reels_limit = max_reels or MAX_REELS
        start_time = time.time()
        result = ScrapeResult()

        self._status(f"🎯 Target: @{target_username} | Max: {reels_limit} reels")

        for attempt in range(1, self.MAX_ATTEMPTS + 1):
            result.attempt_count = attempt
            delay = self.ATTEMPT_DELAYS[attempt - 1] if attempt <= len(self.ATTEMPT_DELAYS) else 10

            if delay > 0:
                self._status(f"⏳ {delay}s kutilmoqda (urinish {attempt})...")
                time.sleep(delay)

            self._status(f"🔄 Urinish {attempt}/{self.MAX_ATTEMPTS}...")

            try:
                profile, reels, error = self._attempt_scrape(target_username, reels_limit)

                if error:
                    self._status(f"❌ Urinish {attempt}: {error[:100]}")
                    result.error = error
                    continue

                if not reels:
                    self._status(f"⚠️ Urinish {attempt}: Reels topilmadi")
                    result.error = "Reels topilmadi — profil yopiq yoki bo'sh"
                    continue

                # Success — analyze
                self._status(f"📊 {len(reels)} ta reel tahlil qilinmoqda...")
                stats, recs, ideas = self._analyze(profile, reels)

                result.success = True
                result.profile = profile
                result.reels = reels
                result.stats = stats
                result.recommendations = recs
                result.ideas = ideas
                result.duration_sec = time.time() - start_time
                result.error = ""

                # Save to memory
                self._save_to_memory(reels, stats)

                # Record health
                self._record_health(True)

                self._status(
                    f"✅ Tayyor! {len(reels)} reels | "
                    f"{result.duration_sec:.0f}s | "
                    f"urinish {attempt}"
                )
                return result

            except Exception as e:
                error_detail = f"{type(e).__name__}: {str(e)[:150]}"
                self._status(f"❌ Urinish {attempt} xato: {error_detail}")
                result.error = error_detail
                logger.error(f"Scrape attempt {attempt} failed: {traceback.format_exc()}")

        # All attempts failed
        result.duration_sec = time.time() - start_time
        self._record_health(False, result.error)
        self._status(f"❌ {self.MAX_ATTEMPTS} urinishdan keyin muvaffaqiyatsiz")
        return result

    def _attempt_scrape(
        self, target: str, max_reels: int
    ) -> Tuple[object, List, str]:
        """
        Single scrape attempt.
        Returns: (profile, reels, error_string)
        """
        import config as cfg
        from browser import InstagramBrowser
        from scraper import ReelsScraper

        # Override config for this run
        old_target = cfg.TARGET_PROFILE
        old_max = cfg.MAX_REELS
        cfg.TARGET_PROFILE = target
        cfg.MAX_REELS = max_reels

        browser = None
        try:
            browser = InstagramBrowser()

            if not browser.login():
                return None, [], "Instagram sessiyasi topilmadi"

            scraper = ReelsScraper(browser)
            profile, reels = scraper.scrape_all_reels()
            browser.close()
            return profile, reels, ""

        except Exception as e:
            if browser:
                try:
                    browser.force_close()
                except Exception:
                    pass
            return None, [], str(e)

        finally:
            cfg.TARGET_PROFILE = old_target
            cfg.MAX_REELS = old_max

    def _analyze(self, profile, reels) -> Tuple[Dict, List[str], List]:
        """Run analysis on scraped data."""
        from analyzer import ReelsAnalyzer
        analyzer = ReelsAnalyzer(profile, reels)
        stats = analyzer.compute_stats()
        recs = analyzer.generate_recommendations()
        ideas = analyzer.generate_reel_ideas(count=20)
        return stats, recs, ideas

    def _save_to_memory(self, reels, stats: Dict) -> None:
        """Auto-save viral hooks and patterns to memory."""
        try:
            avg_views = stats.get("views", {}).get("average", 0)
            account_id = self.account.id

            saved_hooks = 0
            for reel in reels:
                if reel.views > avg_views * 1.5 and reel.caption:
                    # Extract hook (first sentence)
                    hook = reel.caption.split(".")[0].strip()
                    if hook and len(hook) > 10:
                        score = min(10, reel.views / max(avg_views, 1) * 5)
                        memory.save_memory(
                            account_id=account_id,
                            category="hook",
                            content=hook,
                            tags=["scraped", "viral"],
                            score=round(score, 1),
                            source="scraped",
                            metadata={"views": reel.views, "er": reel.engagement_rate},
                        )
                        saved_hooks += 1

            if saved_hooks:
                logger.info(f"🧠 {saved_hooks} ta viral hook xotiraga saqlandi")

        except Exception as e:
            logger.warning(f"Memory saqlashda xato: {e}")

    def _record_health(self, success: bool, error: str = "") -> None:
        """Record to watchdog health system."""
        try:
            from app.ops.watchdog import health
            health.record_scrape(success, error)
        except Exception:
            pass
