#!/usr/bin/python
# -*- coding: utf-8 -*-

# Copyright (c) Christoph Goebel
#
# The Regents of the University of California. All rights reserved.
#
# Redistribution and use in source and binary forms, with or without modification, are permitted provided that the following conditions are met:
#
# Redistributions of source code must retain the above copyright notice, this list of conditions and the following disclaimer.
# Redistributions in binary form must reproduce the above copyright notice, this list of conditions and the following disclaimer in the documentation and/or other materials provided with the distribution.
# All advertising materials mentioning features or use of this software must display the following acknowledgement: "This product includes software developed by the University of California, Berkeley and its contributors."
# Neither the name of the University nor the names of its contributors may be used to endorse or promote products derived from this software without specific prior written permission.
#
# THIS SOFTWARE IS PROVIDED BY THE REGENTS AND CONTRIBUTORS "AS IS" AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING,
# BUT NOT LIMITED TO, THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE DISCLAIMED.
# IN NO EVENT SHALL THE REGENTS OR CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY,
# OR CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES; LOSS OF USE,
# DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT,
# STRICT LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF THIS SOFTWARE,
# EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.

import logging
import os
import subprocess
import sys
import time
from datetime import date

import gpiod  # type: ignore[import-not-found]
import threading
from datetime import timedelta
from gpiod.line import Direction, Edge, Value  # type: ignore[import-not-found]

from .display_manager import DisplayManager

logging.basicConfig(level=logging.WARNING)
logger = logging.getLogger("radio")

current_dir = os.path.realpath(__file__)
parent_dir = os.path.realpath(current_dir + "/../..")

version = "2023.1-xmas"

display_operating_instructions = False

radio_playlist = parent_dir + "/conf/radio_sender.m3u"

PH = "kradio@kradio"

mpc = {
    "clear"         : "mpc -h " + str(PH) + " clear",
    "update"        : "mpc -h " + str(PH) + " update",
    "play"          : "mpc -h " + str(PH) + " play ",
    "stop"          : "mpc -h " + str(PH) + " stop",
    "loadlist"      : "mpc -h " + str(PH) + " load radio_sender",
    "next"          : "mpc -h " + str(PH) + " next",
    "prev"          : "mpc -h " + str(PH) + " prev",
    "volumeup"      : "mpc -h " + str(PH) + " volume +5",
    "volumedown"    : "mpc -h " + str(PH) + " volume -5",
    "volumestartup" : "mpc -h " + str(PH) + " volume 20",
    "shuffle"       : "mpc -h " + str(PH) + " shuffle",
    "addmusic"      : "cd " + parent_dir + "/music && mpc -h " + str(PH) + " add *.*",
    "songinfo"      : "mpc -h " + str(PH) + " current -f '%title%'"
}

# WPA key character sets (used for WiFi configuration mode)
digits: list[str] = ['0','1','2','3','4','5','6','7','8','9']

letters: list[str] = ['A','a','B','b','C','c','D','d','E','e','F','f','G','g','H','h','I','i',
                      'J','j','K','k','L','l','M','m','N','n','O','o','P','p','Q','q','R','r',
                      'S','s','T','t','U','u','V','v','W','w','X','x','Y','y','Z','z']

special_chars: list[str] = [' ','_','!','"','%','&','/','(',')','<','>','|','{','}',
                             '=','?','*',"'",'+','-','#',',','.',';',':','^']

all_chars: list[str] = digits + letters + special_chars
selected_char_idx = 10
current_char = ""
input_buffer = ""


#############################################
# BCM GPIO offsets (BOARD pin equivalents)  #
# BOARD 7->BCM 4, 13->27, 15->22, 16->23,  #
# 29->5, 31->6                              #
#############################################
KeyRight      = 4   # green  (BOARD 7)
KeyLeft       = 23  # yellow (BOARD 16)
KeyOk         = 27  # blue   (BOARD 13)
KeyVolumeUp   = 22  # purple (BOARD 15)
KeyVolumeDown = 5   # grey   (BOARD 29)
KeyStandby    = 6   # white  (BOARD 31)

BUTTON_OFFSETS = [KeyRight, KeyLeft, KeyOk, KeyVolumeUp, KeyVolumeDown, KeyStandby]
GPIO_CHIP = "/dev/gpiochip0"

global mode


####################
# Hardware helpers #
####################
def wifi_on() -> None:
    logger.debug("wifi_on")
    os.system("sudo ip link set wlan0 up")
    time.sleep(5.0)

def wifi_off() -> None:
    # Not switching off because switching back on takes too long.
    pass

def get_ip_display() -> str:
    logger.debug("get_ip_display")
    ip_cmd = "hostname -I | cut -f1 -d' '"
    ip_addr = subprocess.check_output([ip_cmd], shell=True, text=True)
    ip_addr = ip_addr.strip("\n")
    ip_len = len(ip_addr)
    if ip_len > 1:
        return str(ip_addr)
    return "   ---.---.---.---  "


####################
# Mode functions   #
####################
def toggle_radio_mp3(pin: int) -> None:
    logger.debug("toggle_radio_mp3")
    global mode
    if mode == 1:
        mp3_mode()
    update_station_count()
    radio_mode()

def startup_mode() -> None:
    logger.debug("startup_mode")
    os.system(mpc["volumestartup"])
    os.system(mpc["clear"])
    os.system(mpc["update"])
    os.system('mpg321 --gain 20 ' + parent_dir + '/conf/StartUp.mp3')

def radio_mode() -> None:
    logger.debug("radio_mode")
    global mode, current_station
    if (mode == 0) or (mode == 31) or (mode == 32):
        mode = 1
        wifi_on()
        os.system(mpc["volumestartup"])
    mode = 1
    os.system(mpc["clear"])
    os.system(mpc["loadlist"])
    os.system(mpc["play"] + str(current_station))

def mp3_mode() -> None:
    logger.debug("mp3_mode")
    global mode
    mode = 2
    os.system(mpc["update"])
    os.system(mpc["clear"])
    os.system(mpc["addmusic"])
    os.system(mpc["shuffle"])
    os.system(mpc["play"] + "1")

def standby_mode(pin: int) -> None:
    logger.debug("standby_mode")
    global mode, input_buffer
    time.sleep(0.5)  # allow time for chord key detection
    if (_gpio_value(KeyRight) == Value.INACTIVE) and (_gpio_value(KeyStandby) == Value.INACTIVE):
        reboot_mode()
    elif (_gpio_value(KeyLeft) == Value.INACTIVE) and (_gpio_value(KeyStandby) == Value.INACTIVE):
        shutdown_mode()
    elif mode == 32:
        mode = 0
        display.backlight_on()
        radio_mode()
    else:
        mode = 31
        os.system(mpc["stop"])

def reboot_mode() -> None:
    logger.debug("reboot_mode")
    global mode
    mode = 4
    os.system(mpc["stop"])
    os.system('mpg321 ' + parent_dir + '/conf/ShutDown.mp3')

def shutdown_mode() -> None:
    logger.debug("shutdown_mode")
    global mode
    mode = 5
    os.system(mpc["stop"])
    os.system('mpg321 ' + parent_dir + '/conf/ShutDown.mp3')


######################
# Display functions  #
######################
def show(line1: str, line2: str, line3: str, line4: str) -> None:
    display.set(line1, line2, line3, line4)

def show_line(text: str, line: int) -> None:
    display.set_line(line, text)

def display_off() -> None:
    display.backlight_off()

def show_startup_screen(v: str) -> None:
    logger.debug("show_startup_screen")

    if display_operating_instructions:
        show(
            "Operating manual    ",
            "show? Press and hold",
            "      OK button     ",
            "                    ",
        )
        time.sleep(5)
        if (_gpio_value(KeyOk) == Value.INACTIVE):
            show("--------------------", "  Operating manual  ", "   starting...      ", "--------------------")
            time.sleep(4)

            show(">>> > button --->   ", "                    ", "next station / song ", "                    ")
            time.sleep(4)

            show(">>> < button --->   ", "                    ", "prev station / song ", "                    ")
            time.sleep(4)

            show(">>> ^ button --->   ", "                    ", "volume up           ", "                    ")
            time.sleep(4)

            show(">>> v button --->   ", "                    ", "volume down         ", "                    ")
            time.sleep(4)

            show(">>> Ok button --->  ", "                    ", "enter standby       ", "                    ")
            time.sleep(4)

    update_station_count()
    disk_usage_cmd = "df -h | grep /dev/root | awk '{print $5}'"
    disk_usage = subprocess.check_output([disk_usage_cmd], shell=True, text=True)
    disk_usage = disk_usage.strip("\n").replace('%', '')

    show("--------------------", "    RasPi Radio     ", str(v), "--------------------")
    time.sleep(2)

def build_line1() -> str:
    logger.debug("build_line1")
    time_str = time.strftime("%H:%M")
    wifi_cmd = "iwconfig wlan0 | grep Signal | awk '{print $4}' | cut -c8-9"
    try:
        signal_level = int(subprocess.check_output([wifi_cmd], shell=True, text=True))
        if signal_level <= 25 and signal_level > 0:
            signal_bars = "*   "
        elif signal_level > 25 and signal_level < 51:
            signal_bars = "**  "
        elif signal_level > 51 and signal_level < 76:
            signal_bars = "*** "
        elif signal_level >= 76:
            signal_bars = "****"
        else:
            signal_bars = "    "
        return time_str + "           " + signal_bars
    except ValueError:
        time.sleep(4.0)
        return time_str + "               "

def get_stations() -> list[str]:
    logger.debug("get_stations")
    with open(str(radio_playlist), 'r') as f:
        lines = f.readlines()
    return [line.split(',', 1)[1].strip() for line in lines if line.startswith('#EXTINF:')]

def build_line2_radio() -> str:
    logger.debug("build_line2_radio")
    global current_station
    station_cmd = "mpc -h " + str(PH) + " -f %name% | grep playing | cut -c12-13"
    station_str = subprocess.check_output([station_cmd], shell=True, text=True)
    station_str = station_str.strip("\n/")
    if station_str == "":
        return "  Waiting for feed  "
    try:
        station_num = int(station_str)
        current_station = station_num
        station_padded = "0" + str(station_num) if station_num < 10 else str(station_num)
        station_idx = station_num - 1
        station_names = get_stations()
        station_name_len = len(station_names[station_idx])
        if station_name_len > 15:
            station_names[station_idx] = station_names[station_idx][:15]
        elif station_name_len < 15:
            station_names[station_idx] = '{message: <15}'.format(message=station_names[station_idx])
        return "(" + station_padded + ") " + station_names[station_idx]
    except Exception:
        return "Station not found   "

def build_line2_mp3() -> str:
    logger.debug("build_line2_mp3")
    return "      mp3-Mix       "

def build_line3() -> str:
    logger.debug("build_line3")
    song_info = subprocess.check_output([mpc["songinfo"]], shell=True, text=True)
    if "#" not in song_info:
        return song_info.strip("\n").strip().lstrip()
    return "---"

def build_line4() -> str:
    logger.debug("build_line4")
    day_names = ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"]
    day_num = date.today().weekday()
    day_abbr = day_names[day_num]
    date_str = time.strftime("%d.%m.%Y")
    return date_str + "       " + day_abbr

def build_line2_standby() -> str:
    logger.debug("build_line2_standby")
    return "      Standby       "

def build_reboot_screen() -> tuple[str, str, str, str]:
    logger.debug("build_reboot_screen")
    return "--------------------", "      Reboot        ", "    Please wait     ", "--------------------"

def build_shutdown_screen() -> tuple[str, str, str, str]:
    logger.debug("build_shutdown_screen")
    return "--------------------", "    Shutting down   ", "    Please wait     ", "--------------------"

def build_lines23_favorite() -> tuple[str, str]:
    logger.debug("build_lines23_favorite")
    return "     Favourite      ", "      saved!        "

def build_lines23_no_function() -> tuple[str, str]:
    logger.debug("build_lines23_no_function")
    return "   In this mode     ", "  no function!      "

def build_lines23_bookmark() -> tuple[str, str]:
    logger.debug("build_lines23_bookmark")
    return "  Song bookmarked!  ", "smb: conf/merk.txt  "


############################
# Station and song control #
############################
def key_next(pin: int) -> None:
    logger.debug("key_next")
    global current_station, station_count, mode, selected_char_idx
    if mode == 1:
        update_station_count()
        time.sleep(0.3)
        current_station = current_station + 1
        if current_station > station_count:
            current_station = current_station - station_count
        os.system(mpc["play"] + str(current_station))
    elif mode == 2:
        os.system(mpc["next"])

def key_prev(pin: int) -> None:
    logger.debug("key_prev")
    global current_station, station_count, mode, selected_char_idx
    if mode == 1:
        update_station_count()
        time.sleep(0.3)
        current_station = current_station - 1
        if current_station > station_count:
            current_station = current_station - station_count
        elif current_station < 1:
            current_station = station_count
        os.system(mpc["play"] + str(current_station))
    elif mode == 2:
        os.system(mpc["prev"])

def update_station_count() -> None:
    logger.debug("update_station_count")
    global station_count
    station_count = len(get_stations())

def volume_up(pin: int) -> None:
    logger.debug("volume_up")
    os.system(mpc["volumeup"])

def volume_down(pin: int) -> None:
    logger.debug("volume_down")
    os.system(mpc["volumedown"])


####################
# Startup          #
####################
station_count = 0
current_station = 1
mode = 0
display = DisplayManager()
startup_mode()
show_startup_screen(version)
radio_mode()


######################################
# gpiod v2 setup + event thread      #
######################################
_line_settings = gpiod.LineSettings(
    direction=Direction.INPUT,
    edge_detection=Edge.FALLING,
)
_gpio_request = gpiod.request_lines(
    GPIO_CHIP,
    consumer="kradio",
    config={offset: _line_settings for offset in BUTTON_OFFSETS},
)

_KEY_CALLBACKS = {
    KeyRight:      key_next,
    KeyLeft:       key_prev,
    KeyStandby:    standby_mode,
    KeyVolumeUp:   volume_up,
    KeyVolumeDown: volume_down,
}
_BOUNCETIME = 0.2  # seconds — ignore re-triggers within this window
_last_event_time: dict[int, float] = {}

def _gpio_value(offset: int) -> Value:
    return _gpio_request.get_value(offset)

def _event_loop() -> None:
    while True:
        if _gpio_request.wait_edge_events(timedelta(seconds=1)):
            for event in _gpio_request.read_edge_events():
                now = time.monotonic()
                if now - _last_event_time.get(event.line_offset, 0) < _BOUNCETIME:
                    continue
                _last_event_time[event.line_offset] = now
                cb = _KEY_CALLBACKS.get(event.line_offset)
                if cb:
                    cb(event.line_offset)

_event_thread = threading.Thread(target=_event_loop, daemon=True)
_event_thread.start()


################
# Main loop    #
################
logger.debug("Start work loop...")
while True:
    try:
        if mode == 1:
            logger.debug("Mode 1: Radio")
            line1 = build_line1()
            line2 = build_line2_radio()
            line3 = build_line3()
            line4 = build_line4()
            show(line1, line2, line3, line4)
        elif mode == 2:
            logger.debug("Mode 2: MP3 Player")
            line1 = build_line1()
            line2 = build_line2_mp3()
            line3 = build_line3()
            line4 = build_line4()
            show(line1, line2, line3, line4)
        elif mode == 31:
            logger.debug("Mode 31: Going into standby")
            line2 = build_line2_standby()
            show("--------------------", line2, "", "--------------------")
            time.sleep(3.0)
            display_off()
            mode = 32
        elif mode == 32:
            logger.debug("Mode 32: Standby")
            time.sleep(1.0)
        elif mode == 4:
            logger.debug("Mode 4: Reboot")
            show(*build_reboot_screen())
            time.sleep(3.0)
            os.system("sudo reboot")
            time.sleep(3.0)
        elif mode == 5:
            logger.debug("Mode 5: Shutdown")
            show(*build_shutdown_screen())
            time.sleep(3.0)
            os.system("sudo halt")
            sys.exit()
        time.sleep(0.1)

    except KeyboardInterrupt:
        break

_gpio_request.release()
os.system(mpc["stop"])
display_off()
sys.exit()
