"""
Agro AI — Memory Manager Tests
MemoryManager save/load/search testlari.
"""

import pytest

from app.memory.manager import MemoryEntry, MemoryManager


class TestMemoryEntry:
    """MemoryEntry dataclass testlari."""

    def test_create_entry(self):
        entry = MemoryEntry(category="hook", content="Test hook content")
        assert entry.category == "hook"
        assert entry.content == "Test hook content"
        assert entry.id.startswith("hook_")
        assert entry.created_at > 0
        assert entry.score == 0.0

    def test_auto_id_generation(self):
        import time
        e1 = MemoryEntry(category="test", content="a")
        time.sleep(0.002)  # Ensure different millisecond
        e2 = MemoryEntry(category="test", content="b")
        assert e1.id != e2.id


class TestMemoryManager:
    """MemoryManager testlari."""

    def test_save_memory(self):
        mm = MemoryManager()
        entry = mm.save_memory(
            account_id="test_acc",
            category="hook",
            content="Test hook — viral content",
            tags=["test", "viral"],
            score=8.0,
        )
        assert entry.category == "hook"
        assert entry.score == 8.0
        assert "test" in entry.tags

    def test_search_memory(self):
        mm = MemoryManager()
        # Save a few entries
        mm.save_memory("test_search", "hook", "Hook 1", score=9.0)
        mm.save_memory("test_search", "hook", "Hook 2", score=5.0)
        mm.save_memory("test_search", "story", "Story 1", score=7.0)

        # Search by category
        hooks = mm.search_memory("test_search", category="hook")
        assert len(hooks) >= 2
        assert all(h.category == "hook" for h in hooks)

    def test_search_by_min_score(self):
        mm = MemoryManager()
        mm.save_memory("test_score", "hook", "Good hook", score=9.0)
        mm.save_memory("test_score", "hook", "Bad hook", score=2.0)

        results = mm.search_memory("test_score", category="hook", min_score=7.0)
        assert all(r.score >= 7.0 for r in results)

    def test_get_best_patterns(self):
        mm = MemoryManager()
        mm.save_memory("test_best", "hook", "Best hook", score=9.5)
        mm.save_memory("test_best", "hook", "OK hook", score=5.0)

        best = mm.get_best_patterns("test_best", "hook")
        assert isinstance(best, list)

    def test_get_stats(self):
        mm = MemoryManager()
        mm.save_memory("test_stats", "hook", "H1", score=8.0)
        mm.save_memory("test_stats", "story", "S1", score=6.0)

        stats = mm.get_stats("test_stats")
        assert "total" in stats
        assert "categories" in stats
        assert stats["total"] >= 2

    def test_get_learning_context(self):
        mm = MemoryManager()
        mm.save_memory("test_learn", "hook", "Great viral hook", score=9.0)

        ctx = mm.get_learning_context("test_learn", "hook")
        assert isinstance(ctx, str)

    def test_avoid_repetition_context(self):
        mm = MemoryManager()
        mm.save_memory("test_avoid", "hook", "Recent hook content")

        ctx = mm.avoid_repetition_context("test_avoid", "hook")
        assert isinstance(ctx, str)

    def test_update_score(self):
        mm = MemoryManager()
        entry = mm.save_memory("test_update", "hook", "Updatable", score=5.0)
        success = mm.update_score("test_update", entry.id, 9.0)
        assert success is True
