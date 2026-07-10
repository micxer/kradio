import threading
from time import monotonic, sleep

from .lc_display import lcd

LCD_WIDTH = 20
SCROLL_INTERVAL = 0.5  # seconds between scroll advances per row


class DisplayManager:
    """Owns the LCD hardware and writes to it from a background thread.

    The main loop calls set() with full text strings. Rows longer than
    LCD_WIDTH are scrolled automatically; shorter rows are displayed as-is.
    Only changed rows are sent to hardware each cycle.
    """

    def __init__(self) -> None:
        self._lcd = lcd()
        self._desired: dict[int, str] = {1: "", 2: "", 3: "", 4: ""}
        self._written: dict[int, str | None] = {1: None, 2: None, 3: None, 4: None}
        self._scroll_pos: dict[int, int] = {1: 0, 2: 0, 3: 0, 4: 0}
        self._last_scroll: dict[int, float] = {n: monotonic() for n in range(1, 5)}
        self._lock = threading.Lock()
        self._paused = False
        t = threading.Thread(target=self._run, daemon=True)
        t.start()

    def set(self, line1: str, line2: str, line3: str, line4: str) -> None:
        with self._lock:
            new = {1: line1, 2: line2, 3: line3, 4: line4}
            now = monotonic()
            for n, text in new.items():
                if text != self._desired[n]:
                    self._scroll_pos[n] = 0
                    self._last_scroll[n] = now
            self._desired = new

    def set_line(self, n: int, text: str) -> None:
        with self._lock:
            if text != self._desired[n]:
                self._scroll_pos[n] = 0
                self._last_scroll[n] = monotonic()
            self._desired[n] = text

    def backlight_off(self) -> None:
        with self._lock:
            self._paused = True
            self._lcd.backlight_off()

    def backlight_on(self) -> None:
        with self._lock:
            self._lcd.display_on()
            # Invalidate written cache so the worker re-renders all rows,
            # which also restores the backlight as a side effect.
            self._written = {1: None, 2: None, 3: None, 4: None}
            self._paused = False

    def _run(self) -> None:
        while True:
            now = monotonic()
            todo: dict[int, str] = {}

            with self._lock:
                if not self._paused:
                    for n in range(1, 5):
                        text = self._desired[n]
                        if len(text) <= LCD_WIDTH:
                            self._scroll_pos[n] = 0
                            window = text
                        else:
                            interval = SCROLL_INTERVAL * 3 if self._scroll_pos[n] == 0 else SCROLL_INTERVAL
                            if now - self._last_scroll[n] >= interval:
                                self._scroll_pos[n] += 1
                                if self._scroll_pos[n] > len(text) - LCD_WIDTH:
                                    self._scroll_pos[n] = 0
                                self._last_scroll[n] = now
                            pos = self._scroll_pos[n]
                            window = text[pos:pos + LCD_WIDTH]
                        if window != self._written[n]:
                            todo[n] = window

            for n, window in todo.items():
                self._lcd.display_string(window, n)
                with self._lock:
                    self._written[n] = window

            sleep(0.05)
