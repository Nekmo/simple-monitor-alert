#!/usr/bin/env bash
# Smartctl monitor
# Add to sudoers:
# sma ALL= (ALL) NOPASSWD: /usr/sbin/smartctl
# No arguments required.

echo "X-Run-Every-Seconds: 43200"

for disk in `lsblk -d -o name | tail -n +2`; do
    status=`sudo smartctl -H /dev/$disk | tail -n 2 | head -n +1 | awk '{print $NF}'`
    if [[ $status != 'summary' && $? != 1 ]]; then
        echo "smart_status($disk).name = 'SMART test result on /dev/$disk'"
        echo "smart_status($disk).expected = 'PASSED'"
        echo "smart_status($disk).value = '$status'"
    fi
done
