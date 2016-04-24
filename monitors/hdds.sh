#!/usr/bin/env bash

IFS=$'\n'
for part_data in `df -h`; do
    device=$(basename $(echo $part_data | awk '{ print $1 }'));
    if [[ `grep "$device" /proc/partitions` == "" ]]; then
        # Ignore dev, run, tmpfs...
        continue
    fi
    echo "pcnt_use($device).name = 'Percentage of space usted in $device ("`echo $part_data | awk '{ print $6 }'`")'";
    echo "pcnt_use($device).expected = <= 80"
    echo "pcnt_use($device).value = "`echo $part_data | awk '{ print substr($5, 1, length($5)-1) }'`;
    echo -n "pcnt_use($device).extra_info = 'Space: "`echo $part_data | awk '{ print $4 }'`"/";
    echo `echo $part_data | awk '{ print $3 }'`"'"
done