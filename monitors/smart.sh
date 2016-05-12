#!/usr/bin/env bash
# Smartctl monitor
# Add to sudoers:
# sma ALL= (ALL) NOPASSWD: /usr/sbin/smartctl
# No arguments required.

echo "X-Run-Every-Seconds: 43200"

for disk in `lsblk -d -o name | tail -n +2`; do
    status=`sudo smartctl -H /dev/$disk | grep -e 'overall-health' | awk '{print $NF}'`
    if [[ $? != 1 && $status ]]; then
        echo "smart_status.name = 'SMART test result on /dev/$disk'"
        echo "smart_status.expected = 'PASSED'"
        echo "smart_status.value = '$status'"
    fi
done
