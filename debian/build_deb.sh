#!/usr/bin/env bash
set -euo pipefail

VERSION=$(ls dist/kradio-*.whl | grep -oP '(?<=kradio-)[^-]+')

fpm -s dir -t deb \
  -n kradio -v "$VERSION" \
  --architecture all \
  --description "Kitchen web radio" \
  --depends mpd \
  --depends mpc \
  --depends mpg321 \
  --depends alsa-utils \
  --depends i2c-tools \
  --depends python3 \
  --depends python3-pip \
  --depends python3-venv \
  --after-install debian/postinst \
  --before-remove debian/prerm \
  --after-remove debian/postrm \
  --package "dist/kradio_${VERSION}_all.deb" \
  dist/kradio-*.whl=/opt/kradio/ \
  conf/=/opt/kradio/conf/ \
  sys_config/etc/asound.conf=/etc/asound.conf \
  sys_config/etc/mpd.conf=/opt/kradio/etc/mpd.conf \
  sys_config/lib/systemd/system/radio.service=/lib/systemd/system/kradio.service \
  sys_config/lib/systemd/system/LCDaus_text.service=/lib/systemd/system/kradio-lcd-shutdown.service
