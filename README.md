# Internet radio and mp3 player

This is the very simple source code for a small device used as an internet radio for the kitchen. It also can be an mp3
player at the same time. Later on it will be possible to switch it to receiver mode and play music streamed from a
mobile phone or tablet.

It uses a RaspberryPi Zero W together with an [HiFiBerry MiniAmp](https://www.hifiberry.com/shop/boards/miniamp/) and
two Visatron FR 8WP-4WS for sound output. The [HD44780 2004 LCD*](https://amzn.to/3FBBoY8) shows what radio station or
mp3 file is playing.

It can be operated using buttons on the radio itself or via WiFi using a smartphone app.

This is based on an article of the german [Make Magazin 1/19](https://www.heise.de/select/make/2019/1/1551100253897264).

## Installation

Download the latest `kradio_*_all.deb` from the [releases page](../../releases/latest) and install it:

```sh
sudo apt install ./kradio_*_all.deb
```

This installs the app to `/opt/kradio`, creates the `kradio` system user, installs all dependencies, and enables the `kradio` systemd service.

### Verifying build provenance

All release artifacts are signed with [SLSA Build Level 3](https://slsa.dev/spec/v1.0/levels) provenance attestations via GitHub's trusted build infrastructure. Verify before installing:

```sh
gh attestation verify kradio_*_all.deb -R micxer/kradio
```

Requires the [GitHub CLI](https://cli.github.com/).

### Boot configuration

Run the included script to configure `/boot/firmware/config.txt` automatically, then reboot:

```sh
sudo kradio-configure-boot
sudo reboot
```

The script applies required HiFiBerry settings and optional boot optimizations. If you prefer to edit manually:

All settings go in the `[all]` section at the bottom of the file.

**Required — HiFiBerry MiniAmp:**

```ini
[all]
dtparam=i2c_arm=on
dtparam=i2s=on
dtoverlay=hifiberry-dac
```

**Optional — faster boot (headless, no camera, no display):**

```ini
[all]
camera_auto_detect=0      # stop CSI camera probe
display_auto_detect=0     # stop DSI display probe
force_eeprom_read=0       # skip HAT EEPROM probe
dtoverlay=disable-bt      # disable Bluetooth, speeds up UART init
gpu_mem=16                # minimum GPU RAM (no graphics needed)
disable_splash=1          # remove boot splash screen
dtparam=audio=off         # disable bcm2835 audio (kradio uses HiFiBerry)
```

Note: if `dtparam=audio=on` exists earlier in the file, the `dtparam=audio=off` in `[all]` overrides it — sections are cumulative, last write wins.

\* Affiliate Link