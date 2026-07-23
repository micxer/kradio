#!/usr/bin/env bash
set -euo pipefail

WHEEL=$(ls dist/kradio-*.whl)
VERSION=$(echo "$WHEEL" | grep -oP '(?<=kradio-)[^-]+')

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
  "${WHEEL}=/opt/kradio/" \
  conf/=/opt/kradio/conf/ \
  packaging/asound.conf=/etc/asound.conf \
  packaging/mpd.conf=/opt/kradio/etc/mpd.conf \
  packaging/kradio.service=/lib/systemd/system/kradio.service \
  packaging/kradio-lcd-shutdown.service=/lib/systemd/system/kradio-lcd-shutdown.service
