import sys
from types import SimpleNamespace
from unittest.mock import MagicMock

# Stub gpiod before any test imports kradio.radio.
# gpiod is Linux-only and requires real GPIO hardware even on Linux.
_gpiod_mock = MagicMock()
sys.modules["gpiod"] = _gpiod_mock

# Value.INACTIVE/ACTIVE must be concrete sentinels, not MagicMock attributes.
# MagicMock.__eq__ always returns truthy, which would make every chord-key
# comparison in standby_mode() appear to match.
_line_mock = MagicMock()
_line_mock.Value = SimpleNamespace(INACTIVE=0, ACTIVE=1)
_line_mock.Direction = MagicMock()
_line_mock.Edge = MagicMock()
sys.modules["gpiod.line"] = _line_mock
