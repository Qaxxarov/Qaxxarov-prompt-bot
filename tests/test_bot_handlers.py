"""
Agro AI — Bot Handler Tests
Mock Telegram Update bilan handler testlari.
"""

import pytest
from unittest.mock import AsyncMock, MagicMock, patch

from app.bot.router import register, get_registered_sections, _handlers


class TestRouter:
    """Router testlari."""

    def test_register_decorator(self):
        """register() dekoratori handler'ni ro'yxatga oladi."""
        @register("test_section")
        async def test_handler(update, context, action):
            pass

        sections = get_registered_sections()
        assert "test_section" in sections

    def test_registered_sections_not_empty(self):
        """Kamida bir nechta section ro'yxatga olingan."""
        # Import handlers to trigger registration
        from app.bot.handlers import alert_handler, post_handler  # noqa: F401
        sections = get_registered_sections()
        assert len(sections) > 0


class TestMiddleware:
    """Middleware testlari."""

    def test_chunk_short_text(self):
        from app.bot.middleware import _chunk
        result = _chunk("Short text")
        assert len(result) == 1
        assert result[0] == "Short text"

    def test_chunk_long_text(self):
        from app.bot.middleware import _chunk
        long_text = "A" * 5000
        result = _chunk(long_text, max_len=4000)
        assert len(result) == 2
        assert len(result[0]) <= 4000

    def test_chunk_with_newlines(self):
        from app.bot.middleware import _chunk
        text = "\n".join(["Line " + str(i) for i in range(200)])
        result = _chunk(text, max_len=500)
        assert len(result) > 1
        # Har bir chunk 500 dan kichik
        for chunk in result:
            assert len(chunk) <= 500


class TestKeyboards:
    """Keyboard testlari."""

    def test_main_menu(self):
        from app.bot.keyboards import main_menu
        kb = main_menu()
        assert kb is not None
        # ReplyKeyboardMarkup
        assert hasattr(kb, "keyboard")

    def test_tahlil_menu(self):
        from app.bot.keyboards import tahlil_menu
        kb = tahlil_menu()
        assert kb is not None

    def test_alert_menu(self):
        from app.bot.keyboards import alert_menu_kb
        kb = alert_menu_kb()
        assert kb is not None

    def test_post_menu(self):
        from app.bot.keyboards import post_menu_kb
        kb = post_menu_kb()
        assert kb is not None

    def test_product_menu(self):
        from app.bot.keyboards import product_menu_kb
        kb = product_menu_kb()
        assert kb is not None

    def test_back_button(self):
        from app.bot.keyboards import back_button
        kb = back_button()
        assert kb is not None
