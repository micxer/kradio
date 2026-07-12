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

### Manual step: boot configuration

The HiFiBerry MiniAmp requires changes to `/boot/config.txt` that cannot be applied automatically by the package. Apply them once after install by merging the settings from [`packaging/config.txt`](packaging/config.txt) into your `/boot/config.txt`, then reboot.

\* Affiliate Link