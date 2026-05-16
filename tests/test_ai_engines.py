"""
Agro AI — AI Engine Tests
Har bir AI engine: fallback, build_context, generate.
"""

import pytest

from app.ai.base import BaseAIEngine
from app.ai.ab_test import ABTestEngine
from app.ai.sales import SalesEngine
from app.ai.translator import ContentTranslator


class TestBaseAIEngine:
    """BaseAIEngine testlari."""

    def test_init(self, mock_account):
        engine = BaseAIEngine(mock_account)
        assert engine.account == mock_account
        assert engine.engine_name == "base"

    def test_fallback_when_ai_disabled(self, mock_account):
        """AI o'chirilganda fallback matn qaytarishi kerak."""
        engine = BaseAIEngine(mock_account)
        result = engine._fallback("test task")
        assert "AI o'chirilgan" in result
        assert "test task" in result

    @pytest.mark.asyncio
    async def test_generate_fallback(self, mock_account):
        """AI_ENABLED=False bo'lganda generate() fallback qaytaradi."""
        engine = BaseAIEngine(mock_account)
        # AI_ENABLED = False (OPENAI_API_KEY bo'sh)
        result = await engine.generate("test task")
        assert isinstance(result, str)
        assert len(result) > 0

    def test_build_context_basic(self, mock_account):
        """build_context() to'g'ri dict qaytaradi."""
        engine = BaseAIEngine(mock_account)
        ctx = engine.build_context()
        assert isinstance(ctx, dict)
        assert "brand" in ctx
        assert "niche" in ctx
        assert "audience" in ctx
        assert ctx["brand"] == "@test_account"

    def test_build_context_with_stats(self, mock_account):
        """build_context(stats) statistika bilan ishlaydi."""
        engine = BaseAIEngine(mock_account)
        stats = {
            "profile": {"followers": 5000},
            "views": {"average": 1000},
            "engagement": {"average_er": 5.5},
            "content": {"top_hashtags": [{"tag": "#test"}, {"tag": "#agro"}]},
        }
        ctx = engine.build_context(stats)
        assert ctx["followers"] == 5000
        assert ctx["avg_views"] == 1000
        assert ctx["avg_er"] == 5.5

    def test_get_system_prompt(self, mock_account):
        """get_system_prompt() account ma'lumotlarini qaytaradi."""
        engine = BaseAIEngine(mock_account)
        prompt = engine.get_system_prompt()
        assert "@test_account" in prompt
        assert "test niche" in prompt


class TestABTestEngine:
    """ABTestEngine testlari."""

    def test_init(self, mock_account):
        engine = ABTestEngine(mock_account)
        assert engine.engine_name == "ab_test"
        assert engine.default_temperature == 0.9

    def test_get_active_tests_empty(self, mock_account):
        engine = ABTestEngine(mock_account)
        active = engine.get_active_tests()
        assert isinstance(active, list)

    def test_get_stats(self, mock_account):
        engine = ABTestEngine(mock_account)
        stats = engine.get_stats()
        assert "total_tests" in stats
        assert "active" in stats
        assert "completed" in stats


class TestSalesEngine:
    """SalesEngine testlari."""

    def test_init(self, mock_account):
        engine = SalesEngine(mock_account)
        assert engine.engine_name == "sales"

    def test_build_context(self, mock_account):
        engine = SalesEngine(mock_account)
        ctx = engine.build_context()
        assert isinstance(ctx, dict)


class TestContentTranslator:
    """ContentTranslator testlari."""

    def test_init(self, mock_account):
        translator = ContentTranslator(mock_account)
        assert translator.engine_name == "translator"
        assert "uz" in translator.LANGUAGES
        assert "ru" in translator.LANGUAGES

    @pytest.mark.asyncio
    async def test_translate_fallback(self, mock_account):
        """AI o'chirilganda fallback."""
        translator = ContentTranslator(mock_account)
        result = await translator.translate("Test matn", target_lang="ru")
        assert isinstance(result, str)
        assert len(result) > 0
