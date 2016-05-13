#!/usr/bin/env bash
# Add to sudoers:
# sma ALL= (ALL) NOPASSWD: /usr/sbin/hddtemp
# No arguments required.
echo "X-Run-Every-Seconds: 1800"

re='^[0-9]+$'
IFS=$'\n'
for disk in `lsblk -d -o name | tail -n +2`; do
    temp=`sudo hddtemp -n /dev/$disk 2> /dev/null`
    if [[ $temp =~ $re ]]; then
        echo "hdd_temp($disk).name = 'HDD temperature result on /dev/$disk'"
        echo "hdd_temp($disk).expected = <= 46"
        echo "hdd_temp($disk).value = $temp"
    fi
done
