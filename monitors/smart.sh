#!/usr/bin/env bash
# Smartctl monitor
# Add to sudoers (/etc/sudoers)
# sma ALL= (ALL) NOPASSWD: /usr/sbin/smartctl
# No arguments required.
# You must have installed: smartmontools & sudo
# Debian/Ubuntu: apt-get install smartmontools
# Debian: apt-get install sudo
# Fedora: yum install smartmontools
# Arch: pacman -S smartmontools sudo



echo "X-Run-Every-Seconds: 43200"

for disk in `lsblk -d -o name | tail -n +2`; do
    status=`sudo smartctl -H /dev/$disk | grep -e 'overall-health' | awk '{print $NF}'`
    if [[ $? != 1 && $status ]]; then
        echo "smart_status($disk).name = 'SMART test result on /dev/$disk'"
        echo "smart_status($disk).expected = 'PASSED'"
        echo "smart_status($disk).value = '$status'"
    fi
done
