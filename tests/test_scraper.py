"""
Agro AI — Scraper Tests
Mock browser bilan scraping test (import va konfiguratsiya).
"""

import pytest
from unittest.mock import MagicMock, patch

from app.settings import (
    CHROME_PROFILE_DIR,
    CHROME_USER_DATA_DIR,
    HEADLESS,
    MAX_REELS,
    TARGET_PROFILE,
)


class TestScraperConfig:
    """Scraper konfiguratsiya testlari."""

    def test_target_profile_set(self):
        assert TARGET_PROFILE != ""

    def test_max_reels_positive(self):
        assert MAX_REELS > 0
        assert MAX_REELS <= 100

    def test_chrome_profile_set(self):
        assert CHROME_PROFILE_DIR != ""

    def test_headless_is_bool(self):
        assert isinstance(HEADLESS, bool)


class TestScraperPipeline:
    """ScrapingPipeline import va init testlari."""

    def test_import(self):
        """ScrapingPipeline import qilinadi."""
        from app.scraper.pipeline import ScrapingPipeline
        assert ScrapingPipeline is not None

    def test_init(self):
        """ScrapingPipeline init ishlaydi."""
        from app.scraper.pipeline import ScrapingPipeline
        pipeline = ScrapingPipeline()
        assert pipeline is not None
