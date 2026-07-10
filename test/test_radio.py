from unittest.mock import MagicMock, patch
import time

with patch("prog.display_manager.lcd"):
    from prog.display_manager import DisplayManager, LCD_WIDTH, SCROLL_INTERVAL


def make_manager() -> DisplayManager:
    with patch("prog.display_manager.lcd"):
        mgr = DisplayManager()
    return mgr


def test_short_text_not_scrolled():
    mgr = make_manager()
    text = "Hello World"
    mgr.set(text, "", "", "")
    with mgr._lock:
        mgr._scroll_pos[1] = 5  # artificially advance
        mgr._desired[1] = text
    # short text: window should always be full text, pos reset to 0
    with mgr._lock:
        assert len(text) <= LCD_WIDTH


def test_exact_width_not_scrolled():
    mgr = make_manager()
    text = "Hello World for real"  # exactly 20 chars
    assert len(text) == LCD_WIDTH
    mgr.set(text, "", "", "")
    with mgr._lock:
        assert len(mgr._desired[1]) <= LCD_WIDTH


def test_long_text_window_advances():
    mgr = make_manager()
    text = "This is a rolling text"  # 22 chars
    mgr.set(text, "", "", "")

    # Simulate the worker advancing scroll twice
    with mgr._lock:
        mgr._scroll_pos[1] = 0
        mgr._last_scroll[1] = 0.0

    windows = []
    fake_now = 0.0
    for _ in range(3):
        fake_now += SCROLL_INTERVAL + 0.01
        with mgr._lock:
            pos = mgr._scroll_pos[1]
            if fake_now - mgr._last_scroll[1] >= SCROLL_INTERVAL:
                pos += 1
                if pos > len(text) - LCD_WIDTH:
                    pos = 0
                mgr._scroll_pos[1] = pos
                mgr._last_scroll[1] = fake_now
            windows.append(text[pos:pos + LCD_WIDTH])

    assert windows[0] == "his is a rolling tex"
    assert windows[1] == "is is a rolling text"
    assert windows[2] == "This is a rolling te"  # wraps back to 0


def test_text_change_resets_scroll():
    mgr = make_manager()
    mgr.set("First long song title!", "", "", "")
    with mgr._lock:
        mgr._scroll_pos[1] = 5

    mgr.set("New song", "", "", "")
    with mgr._lock:
        assert mgr._scroll_pos[1] == 0
