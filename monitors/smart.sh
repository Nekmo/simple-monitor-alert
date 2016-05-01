#!/usr/bin/env bash
# Smartctl monitor

for disk in `lsblk -d -o name | tail -n +2`; do
    status=`sudo smartctl -H /dev/$disk | tail -n 2 | head -n +1 | awk '{print $NF}'`
    if [[ $status != 'summary' && $? != 1 ]]; then
        echo "smart_status.name = 'SMART test result on /dev/$disk'"
        echo "smart_status.expected = 'PASSED'"
        echo "smart_status.value = '$status'"
    fi
done
