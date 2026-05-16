"""
Agro AI — Test Fixtures
pytest fixtures: mock Account, mock OpenAI, temp data dirs.
"""

import json
import os
import sys
import tempfile
from pathlib import Path
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

# Loyiha ildizini path'ga qo'shish
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

# Test uchun DATA_DIR ni vaqtincha papkaga yo'naltirish
os.environ.setdefault("TELEGRAM_BOT_TOKEN", "test_token_123:ABC")
os.environ.setdefault("OPENAI_API_KEY", "")  # AI o'chirilgan holda test
os.environ.setdefault("ALLOWED_USER_IDS", "123456789")
os.environ.setdefault("TARGET_PROFILE", "test_account")


@pytest.fixture
def mock_account():
    """Test uchun mock Account."""
    from app.accounts import Account
    return Account(
        id="test_account",
        instagram="@test_account",
        niche="test niche — agro",
        target_audience="test audience — fermerlar",
        language="uz",
        languages=["uz", "ru"],
        chrome_profile="Default",
        ai_personality="Test AI personality",
        hashtags=["#test", "#agro"],
        posting_times=["19:00", "20:00"],
    )


@pytest.fixture
def temp_data_dir(tmp_path):
    """Vaqtincha data papkasi."""
    data_dir = tmp_path / "data"
    data_dir.mkdir()
    (data_dir / "memory").mkdir()
    (data_dir / "alerts").mkdir()
    return data_dir


@pytest.fixture
def mock_openai_response():
    """Mock OpenAI API response."""
    mock_response = MagicMock()
    mock_response.choices = [MagicMock()]
    mock_response.choices[0].message.content = "Test AI javob — hook, caption, hashtag"
    return mock_response


@pytest.fixture
def mock_openai_client(mock_openai_response):
    """Mock AsyncOpenAI client."""
    client = AsyncMock()
    client.chat.completions.create = AsyncMock(return_value=mock_openai_response)
    return client


@pytest.fixture
def sample_products_data(tmp_path):
    """Test uchun products.json."""
    products_file = tmp_path / "products.json"
    data = {
        "products": [
            {
                "id": "test_product_1",
                "name": "Test Pomidor",
                "category": "urug'lar",
                "price": 25000,
                "currency": "UZS",
                "stock": 100,
                "description": "Test mahsulot",
                "best_season": "mart-aprel",
                "image_url": "",
                "tags": ["test", "pomidor"],
                "active": True,
                "created_at": 0,
                "updated_at": 0,
            }
        ]
    }
    products_file.write_text(json.dumps(data, ensure_ascii=False), encoding="utf-8")
    return products_file
