import threading
from time import sleep

from .lc_display import lcd


class DisplayManager:
    """Owns the LCD hardware and writes to it from a background thread.

    The main loop calls set() to declare desired display content and returns
    immediately. The background thread detects which rows changed and sends
    only those to the hardware.
    """

    def __init__(self) -> None:
        self._lcd = lcd()
        self._desired: dict[int, str] = {1: "", 2: "", 3: "", 4: ""}
        self._written: dict[int, str | None] = {1: None, 2: None, 3: None, 4: None}
        self._lock = threading.Lock()
        self._paused = False
        t = threading.Thread(target=self._run, daemon=True)
        t.start()

    def set(self, line1: str, line2: str, line3: str, line4: str) -> None:
        with self._lock:
            self._desired = {1: line1, 2: line2, 3: line3, 4: line4}

    def set_line(self, n: int, text: str) -> None:
        with self._lock:
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
            with self._lock:
                if self._paused:
                    todo: dict[int, str] = {}
                else:
                    todo = {
                        n: t
                        for n, t in self._desired.items()
                        if t != self._written[n]
                    }
            for n, text in todo.items():
                self._lcd.display_string(text, n)
                with self._lock:
                    self._written[n] = text
            sleep(0.05)
