import pytest
from unittest.mock import MagicMock, mock_open, patch

import kradio.radio as radio

# ---------------------------------------------------------------------------
# M3U fixture used across multiple test groups
# ---------------------------------------------------------------------------
M3U = """\
#EXTM3U
#EXTINF:-1,Bayern 1
https://example.com/s1
#EXTINF:-1,BR 24
https://example.com/s2
#EXTINF:-1,Exact15Chars!!
https://example.com/s3
#EXTINF:-1,This Name Is Way Over 15 Characters Long
https://example.com/s4
"""

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------
def _mock_display():
    return MagicMock()


# ---------------------------------------------------------------------------
# get_stations()
# ---------------------------------------------------------------------------
class TestGetStations:
    def test_returns_names_from_extinf_lines(self):
        with patch("builtins.open", mock_open(read_data=M3U)):
            stations = radio.get_stations()
        assert stations == [
            "Bayern 1",
            "BR 24",
            "Exact15Chars!!",
            "This Name Is Way Over 15 Characters Long",
        ]

    def test_ignores_url_and_comment_lines(self):
        with patch("builtins.open", mock_open(read_data=M3U)):
            stations = radio.get_stations()
        for s in stations:
            assert not s.startswith("http")
            assert not s.startswith("#EXTM3U")

    def test_empty_file_returns_empty_list(self):
        with patch("builtins.open", mock_open(read_data="")):
            stations = radio.get_stations()
        assert stations == []


# ---------------------------------------------------------------------------
# build_line1() — WiFi signal bars
# ---------------------------------------------------------------------------
@pytest.mark.parametrize("signal,expected_bars", [
    (0,   "    "),   # zero: not > 0
    (1,   "*   "),   # lower bound of tier 1
    (25,  "*   "),   # upper bound of tier 1
    (26,  "**  "),   # lower bound of tier 2
    (50,  "**  "),   # 50 < 51
    (51,  "**  "),   # boundary fixed: was a gap in original code
    (52,  "*** "),   # lower bound of tier 3
    (75,  "*** "),   # 75 < 76
    (76,  "****"),   # lower bound of tier 4
    (100, "****"),   # well above threshold
])
def test_build_line1_signal_bars(signal: int, expected_bars: str):
    with patch("kradio.radio.subprocess.check_output", return_value=str(signal)), \
         patch("kradio.radio.time.strftime", return_value="12:00"):
        result = radio.build_line1()
    assert result.endswith(expected_bars)

def test_build_line1_non_numeric_returns_fallback():
    with patch("kradio.radio.subprocess.check_output", return_value="  "), \
         patch("kradio.radio.time.strftime", return_value="08:30"), \
         patch("kradio.radio.time.sleep"):
        result = radio.build_line1()
    assert result.startswith("08:30")
    assert "   " in result  # no bars, just spaces

def test_build_line1_result_is_20_chars():
    with patch("kradio.radio.subprocess.check_output", return_value="60"), \
         patch("kradio.radio.time.strftime", return_value="12:00"):
        result = radio.build_line1()
    assert len(result) == 20


# ---------------------------------------------------------------------------
# build_line2_radio()
# ---------------------------------------------------------------------------
class TestBuildLine2Radio:
    def _call(self, mpc_output: str, m3u: str = M3U) -> str:
        with patch("kradio.radio.subprocess.check_output", return_value=mpc_output), \
             patch("builtins.open", mock_open(read_data=m3u)):
            return radio.build_line2_radio()

    def test_empty_output_shows_waiting(self):
        assert self._call("\n") == "  Waiting for feed  "

    def test_single_digit_station_padded(self):
        result = self._call("1\n")
        assert result.startswith("(01) ")
        assert len(result) == 20

    def test_two_digit_station_no_extra_pad(self):
        result = self._call("2\n")
        assert result.startswith("(02) ")

    def test_name_exactly_15_not_truncated(self):
        # "Exact15Chars!!" is 14 chars — make a 15-char name
        m3u_15 = "#EXTM3U\n#EXTINF:-1,Exactly15Chars\nhttps://x.com/s1\n"
        result = self._call("1\n", m3u=m3u_15)
        assert "Exactly15Chars" in result

    def test_name_over_15_truncated(self):
        result = self._call("4\n")
        # station 4 name is "This Name Is Way Over 15 Characters Long" (>15)
        # must be cut to 15 chars; prefix "(04) " is 5 chars
        name_part = result[5:]
        assert len(name_part) == 15

    def test_non_numeric_returns_not_found(self):
        result = self._call("abc\n")
        assert result == "Station not found   "


# ---------------------------------------------------------------------------
# build_line3()
# ---------------------------------------------------------------------------
class TestBuildLine3:
    def test_normal_song_stripped(self):
        with patch("kradio.radio.subprocess.check_output", return_value="  My Song  \n"):
            assert radio.build_line3() == "My Song"

    def test_hash_in_output_returns_dash(self):
        with patch("kradio.radio.subprocess.check_output", return_value="http://stream/#tag\n"):
            assert radio.build_line3() == "---"

    def test_empty_string(self):
        with patch("kradio.radio.subprocess.check_output", return_value="\n"):
            assert radio.build_line3() == ""

    def test_extinf_style_hash_triggers_filter(self):
        with patch("kradio.radio.subprocess.check_output", return_value="#EXTINF:-1,title\n"):
            assert radio.build_line3() == "---"


# ---------------------------------------------------------------------------
# build_line4()
# ---------------------------------------------------------------------------
@pytest.mark.parametrize("weekday,abbr", [
    (0, "Mon"), (1, "Tue"), (2, "Wed"), (3, "Thu"),
    (4, "Fri"), (5, "Sat"), (6, "Sun"),
])
def test_build_line4_weekday_abbreviation(weekday: int, abbr: str):
    mock_date = MagicMock()
    mock_date.weekday.return_value = weekday
    with patch("kradio.radio.date") as mock_date_cls, \
         patch("kradio.radio.time.strftime", return_value="12.07.2025"):
        mock_date_cls.today.return_value = mock_date
        result = radio.build_line4()
    assert abbr in result
    assert "12.07.2025" in result


# ---------------------------------------------------------------------------
# get_ip_display()
# ---------------------------------------------------------------------------
class TestGetIpDisplay:
    def test_returns_stripped_ip(self):
        with patch("kradio.radio.subprocess.check_output", return_value="192.168.1.100\n"):
            assert radio.get_ip_display() == "192.168.1.100"

    def test_empty_output_returns_placeholder(self):
        with patch("kradio.radio.subprocess.check_output", return_value="\n"):
            assert radio.get_ip_display() == "   ---.---.---.---  "

    def test_single_char_treated_as_empty(self):
        # len("a") == 1, not > 1 → placeholder
        with patch("kradio.radio.subprocess.check_output", return_value="a\n"):
            assert radio.get_ip_display() == "   ---.---.---.---  "


# ---------------------------------------------------------------------------
# key_next()
# ---------------------------------------------------------------------------
class TestKeyNext:
    def setup_method(self):
        radio.mode = radio.MODE_RADIO
        radio.current_station = 3
        radio.station_count = 5

    def test_advances_station(self):
        with patch("kradio.radio.os.system"), \
             patch("kradio.radio.time.sleep"), \
             patch("builtins.open", mock_open(read_data=M3U)):
            radio.key_next(4)
        assert radio.current_station == 4

    def test_wraps_forward_at_end(self):
        # M3U has 4 stations; key_next calls update_station_count() so
        # station_count becomes 4. Start at 4 → 4+1=5 > 4 → 5-4=1.
        radio.current_station = 4
        with patch("kradio.radio.os.system"), \
             patch("kradio.radio.time.sleep"), \
             patch("builtins.open", mock_open(read_data=M3U)):
            radio.key_next(4)
        assert radio.current_station == 1

    def test_calls_mpc_play(self):
        with patch("kradio.radio.os.system") as mock_sys, \
             patch("kradio.radio.time.sleep"), \
             patch("builtins.open", mock_open(read_data=M3U)):
            radio.key_next(4)
        calls = [str(c) for c in mock_sys.call_args_list]
        assert any("play" in c for c in calls)

    def test_mode2_calls_mpc_next(self):
        radio.mode = radio.MODE_MP3
        with patch("kradio.radio.os.system") as mock_sys:
            radio.key_next(4)
        mock_sys.assert_called_once_with(radio.mpc["next"])

    def test_other_mode_does_nothing(self):
        radio.mode = radio.MODE_INIT
        with patch("kradio.radio.os.system") as mock_sys:
            radio.key_next(4)
        mock_sys.assert_not_called()


# ---------------------------------------------------------------------------
# key_prev()
# ---------------------------------------------------------------------------
class TestKeyPrev:
    def setup_method(self):
        radio.mode = radio.MODE_RADIO
        radio.current_station = 3
        radio.station_count = 5

    def test_decrements_station(self):
        with patch("kradio.radio.os.system"), \
             patch("kradio.radio.time.sleep"), \
             patch("builtins.open", mock_open(read_data=M3U)):
            radio.key_prev(23)
        assert radio.current_station == 2

    def test_wraps_backward_at_start(self):
        # M3U has 4 stations; key_prev calls update_station_count() so
        # station_count becomes 4. Start at 1 → 1-1=0 < 1 → station_count=4.
        radio.current_station = 1
        with patch("kradio.radio.os.system"), \
             patch("kradio.radio.time.sleep"), \
             patch("builtins.open", mock_open(read_data=M3U)):
            radio.key_prev(23)
        assert radio.current_station == 4

    def test_over_count_branch(self):
        # M3U has 4 stations; station_count becomes 4 after update_station_count().
        # Start at 6 → 6-1=5 > 4 → 5-4=1.
        radio.current_station = 6
        with patch("kradio.radio.os.system"), \
             patch("kradio.radio.time.sleep"), \
             patch("builtins.open", mock_open(read_data=M3U)):
            radio.key_prev(23)
        assert radio.current_station == 1

    def test_mode2_calls_mpc_prev(self):
        radio.mode = radio.MODE_MP3
        with patch("kradio.radio.os.system") as mock_sys:
            radio.key_prev(23)
        mock_sys.assert_called_once_with(radio.mpc["prev"])

    def test_other_mode_does_nothing(self):
        radio.mode = radio.MODE_INIT
        with patch("kradio.radio.os.system") as mock_sys:
            radio.key_prev(23)
        mock_sys.assert_not_called()


# ---------------------------------------------------------------------------
# standby_mode()
# ---------------------------------------------------------------------------
class TestStandbyMode:
    INACTIVE = 0
    ACTIVE = 1

    def setup_method(self):
        radio.mode = radio.MODE_RADIO
        radio.display = _mock_display()

    def test_right_plus_standby_chord_reboots(self):
        # Both KeyRight and KeyStandby are INACTIVE → reboot
        with patch("kradio.radio._gpio_value", return_value=self.INACTIVE), \
             patch("kradio.radio.reboot_mode") as mock_reboot, \
             patch("kradio.radio.time.sleep"):
            radio.standby_mode(6)
        mock_reboot.assert_called_once()

    def test_left_plus_standby_chord_shuts_down(self):
        # KeyRight ACTIVE, KeyLeft INACTIVE, KeyStandby INACTIVE → shutdown
        def gpio_side_effect(offset: int) -> int:
            return self.INACTIVE if offset in (radio.KeyLeft, radio.KeyStandby) else self.ACTIVE

        with patch("kradio.radio._gpio_value", side_effect=gpio_side_effect), \
             patch("kradio.radio.shutdown_mode") as mock_shutdown, \
             patch("kradio.radio.time.sleep"):
            radio.standby_mode(6)
        mock_shutdown.assert_called_once()

    def test_mode32_resumes_radio(self):
        radio.mode = radio.MODE_STANDBY
        with patch("kradio.radio._gpio_value", return_value=self.ACTIVE), \
             patch("kradio.radio.radio_mode") as mock_radio, \
             patch("kradio.radio.time.sleep"):
            radio.standby_mode(6)
        assert radio.mode == radio.MODE_INIT
        radio.display.backlight_on.assert_called_once()
        mock_radio.assert_called_once()

    def test_default_enters_standby(self):
        radio.mode = radio.MODE_RADIO
        with patch("kradio.radio._gpio_value", return_value=self.ACTIVE), \
             patch("kradio.radio.os.system") as mock_sys, \
             patch("kradio.radio.time.sleep"):
            radio.standby_mode(6)
        assert radio.mode == radio.MODE_ENTERING_STANDBY
        mock_sys.assert_called_once_with(radio.mpc["stop"])


# ---------------------------------------------------------------------------
# update_station_count()
# ---------------------------------------------------------------------------
class TestUpdateStationCount:
    def test_sets_global_from_m3u(self):
        with patch("builtins.open", mock_open(read_data=M3U)):
            radio.update_station_count()
        assert radio.station_count == 4  # M3U has 4 #EXTINF lines

    def test_empty_file_sets_zero(self):
        with patch("builtins.open", mock_open(read_data="")):
            radio.update_station_count()
        assert radio.station_count == 0
