#!/bin/bash -x

# apply boot config
if ! diff -w sys_config/boot/config.txt /boot/config.txt > /dev/null
then
    sudo cp --backup=numbered sys_config/boot/config.txt /boot/config.txt
fi

# install necessary software
sudo apt install -y mpd mpc mpg321 alsa-utils python3-pip i2c-tools

# create necessary firs
mkdir -p /home/kradio/raspiradio/music

# copy config files
if ! diff -w sys_config/etc/asound.conf /etc/asound.conf > /dev/null
then
    sudo cp --backup=numbered sys_config/etc/asound.conf /etc/asound.conf
fi
if ! diff -w sys_config/etc/mpd.conf /etc/mpd.conf > /dev/null
then
    sudo cp --backup=numbered sys_config/etc/mpd.conf /etc/mpd.conf
fi

# copy init script
if ! diff -w sys_config/etc/init.d/radio /etc/init.d/radio > /dev/null
then
    sudo cp --backup=numbered sys_config/etc/init.d/radio /etc/init.d/radio
    sudo chmod 755 /etc/init.d/radio
    sudo update-rc.d radio defaults
fi

# Python dependencies
#pip install -r requirements.txt
