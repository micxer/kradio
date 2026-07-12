#!/bin/bash -x

# apply boot config
if ! diff -w packaging/config.txt /boot/config.txt > /dev/null
then
    echo "Install updated config.txt"
    sudo cp --backup=numbered packaging/config.txt /boot/config.txt
fi

# install necessary software
sudo apt install -y mpd mpc mpg321 alsa-utils python3-pip i2c-tools

# create necessary firs
mkdir -p /home/kradio/raspiradio/music

# copy config files
if ! diff -w packaging/asound.conf /etc/asound.conf > /dev/null
then
    echo "Install updated asound.conf"
    sudo cp --backup=numbered packaging/asound.conf /etc/asound.conf
fi
if ! diff -w packaging/mpd.conf /etc/mpd.conf > /dev/null
then
    echo "Install updated mpd.conf"
    sudo cp --backup=numbered packaging/mpd.conf /etc/mpd.conf
fi

# copy init script
if ! diff -w packaging/kradio.service /etc/systemd/system/kradio.service > /dev/null
then
    echo "Install updated systemd service"
    sudo cp --backup=numbered packaging/kradio.service /etc/systemd/system/kradio.service
    sudo systemctl daemon-reload
    sudo systemctl enable kradio.service
fi

# Python dependencies
uv sync

sudo systemctl restart kradio.service
