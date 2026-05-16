"""
Agro AI — Account Tests
AccountManager CRUD testlari.
"""

import json
import tempfile
from pathlib import Path
from unittest.mock import patch

import pytest

from app.accounts import Account, AccountManager


class TestAccount:
    """Account dataclass testlari."""

    def test_create_account(self):
        acc = Account(id="test", instagram="@test")
        assert acc.id == "test"
        assert acc.instagram == "@test"
        assert acc.language == "uz"
        assert acc.active is True

    def test_username_property(self):
        acc = Account(id="test", instagram="@my_account")
        assert acc.username == "my_account"

    def test_username_without_at(self):
        acc = Account(id="test", instagram="my_account")
        assert acc.username == "my_account"

    def test_get_system_prompt(self):
        acc = Account(
            id="test",
            instagram="@agro_test",
            niche="agro niche",
            target_audience="fermerlar",
        )
        prompt = acc.get_system_prompt()
        assert "@agro_test" in prompt
        assert "agro niche" in prompt
        assert "fermerlar" in prompt

    def test_default_content_mix(self):
        acc = Account(id="test", instagram="@test")
        assert "educational" in acc.content_mix
        assert "entertainment" in acc.content_mix
        assert sum(acc.content_mix.values()) == 100

    def test_languages_field(self):
        acc = Account(id="test", instagram="@test", languages=["uz", "ru"])
        assert "uz" in acc.languages
        assert "ru" in acc.languages


class TestAccountManager:
    """AccountManager testlari."""

    def test_active_account_exists(self):
        """Har doim faol akkaunt bo'lishi kerak."""
        from app.accounts import accounts
        acc = accounts.active
        assert acc is not None
        assert acc.id != ""
        assert acc.instagram != ""

    def test_all_accounts(self):
        """all_accounts ro'yxat qaytaradi."""
        from app.accounts import accounts
        all_accs = accounts.all_accounts
        assert isinstance(all_accs, list)
        assert len(all_accs) >= 1
