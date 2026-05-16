"""
Agro AI — Alert Manager Tests
AlertManager trigger testlari.
"""

import pytest

from app.ops.alerts import Alert, AlertManager, AlertSettings


class TestAlert:
    """Alert dataclass testlari."""

    def test_create_alert(self):
        alert = Alert(alert_type="viral_reel", message="Test alert")
        assert alert.alert_type == "viral_reel"
        assert alert.message == "Test alert"
        assert alert.id.startswith("alert_")
        assert alert.timestamp > 0
        assert alert.sent is False


class TestAlertSettings:
    """AlertSettings testlari."""

    def test_default_settings(self):
        s = AlertSettings()
        assert s.enabled is True
        assert s.follower_milestone is True
        assert s.viral_reel is True
        assert s.er_drop is True
        assert s.er_spike is True
        assert s.no_post is True
        assert s.best_time is True


class TestAlertManager:
    """AlertManager trigger testlari."""

    def test_init(self):
        mgr = AlertManager("test_alerts")
        assert mgr.account_id == "test_alerts"

    def test_follower_milestone_triggered(self):
        mgr = AlertManager("test_milestone")
        alert = mgr.check_follower_milestone(current_followers=1000, prev_followers=990)
        assert alert is not None
        assert alert.alert_type == "follower_milestone"
        assert "1,000" in alert.message

    def test_follower_milestone_not_triggered(self):
        mgr = AlertManager("test_no_milestone")
        alert = mgr.check_follower_milestone(current_followers=1500, prev_followers=1400)
        assert alert is None

    def test_viral_reel_triggered(self):
        mgr = AlertManager("test_viral")
        alert = mgr.check_viral_reel(reel_views=30000, avg_views=5000)
        assert alert is not None
        assert alert.alert_type == "viral_reel"
        assert "30,000" in alert.message

    def test_viral_reel_not_triggered(self):
        mgr = AlertManager("test_no_viral")
        alert = mgr.check_viral_reel(reel_views=8000, avg_views=5000)
        assert alert is None  # 8000 < 5000*3

    def test_er_drop_triggered(self):
        mgr = AlertManager("test_er_drop")
        alert = mgr.check_er_drop(current_er=3.0, prev_er=5.0)
        assert alert is not None
        assert alert.alert_type == "er_drop"

    def test_er_drop_not_triggered(self):
        mgr = AlertManager("test_no_er_drop")
        alert = mgr.check_er_drop(current_er=4.5, prev_er=5.0)
        assert alert is None  # 10% < 20%

    def test_er_spike_triggered(self):
        mgr = AlertManager("test_er_spike")
        alert = mgr.check_er_spike(current_er=9.0, prev_er=5.0)
        assert alert is not None
        assert alert.alert_type == "er_spike"

    def test_no_post_triggered(self):
        import uuid
        mgr = AlertManager(f"test_no_post_{uuid.uuid4().hex[:6]}")
        alert = mgr.check_no_post(hours_since_last_post=50)
        assert alert is not None
        assert alert.alert_type == "no_post"

    def test_no_post_not_triggered(self):
        mgr = AlertManager("test_no_post_ok")
        alert = mgr.check_no_post(hours_since_last_post=24)
        assert alert is None

    def test_toggle_alert(self):
        mgr = AlertManager("test_toggle")
        # Toggle off
        new_state = mgr.toggle_alert("viral_reel")
        assert new_state is False
        # Toggle back on
        new_state = mgr.toggle_alert("viral_reel")
        assert new_state is True

    def test_get_history(self):
        mgr = AlertManager("test_history")
        mgr.check_follower_milestone(1000, 900)
        history = mgr.get_history()
        assert isinstance(history, list)

    def test_format_settings(self):
        mgr = AlertManager("test_format")
        text = mgr.format_settings()
        assert "ALERT SOZLAMALARI" in text
        assert "Follower milestone" in text
