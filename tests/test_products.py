"""
Agro AI — Product Catalog Tests
ProductCatalog CRUD testlari.
"""

import json
import tempfile
from pathlib import Path
from unittest.mock import patch

import pytest

from app.products.catalog import Product, ProductCatalog


class TestProduct:
    """Product dataclass testlari."""

    def test_create_product(self):
        p = Product(id="test_1", name="Test Product", price=10000)
        assert p.id == "test_1"
        assert p.name == "Test Product"
        assert p.price == 10000
        assert p.active is True
        assert p.created_at > 0

    def test_default_currency(self):
        p = Product(id="test", name="Test")
        assert p.currency == "UZS"


class TestProductCatalog:
    """ProductCatalog CRUD testlari."""

    def test_catalog_loads(self):
        """Katalog yuklanadi."""
        cat = ProductCatalog()
        products = cat.get_all()
        assert isinstance(products, list)

    def test_get_all_returns_list(self):
        cat = ProductCatalog()
        result = cat.get_all()
        assert isinstance(result, list)

    def test_get_in_stock(self):
        cat = ProductCatalog()
        in_stock = cat.get_in_stock()
        assert isinstance(in_stock, list)
        for p in in_stock:
            assert p.stock > 0

    def test_search(self):
        cat = ProductCatalog()
        # Default mahsulotlar bor bo'lishi kerak
        results = cat.search("pomidor")
        assert isinstance(results, list)

    def test_format_product(self):
        cat = ProductCatalog()
        p = Product(id="test", name="Test Product", price=25000, stock=100)
        formatted = cat.format_product(p)
        assert "Test Product" in formatted
        assert "25,000" in formatted

    def test_format_list(self):
        cat = ProductCatalog()
        formatted = cat.format_list()
        assert isinstance(formatted, str)

    def test_get_for_ai_context(self):
        cat = ProductCatalog()
        ctx = cat.get_for_ai_context()
        assert isinstance(ctx, str)
