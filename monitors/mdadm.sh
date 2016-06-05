#!/usr/bin/env bash
# Mdadm monitor
# Check that no RAIDS is degraded.
# No parameters required.
# It only works with softraid (mdadm).
# This monitor will not care if you do not have RAIDs.

if [[ ! -f /proc/mdstat ]]; then
    exit 0;
fi

IFS=$'\n'
for line in `cat /proc/mdstat | tail -n +2 | head -n -1`; do
    if [[ ${line:0:1} != ' ' ]]; then
        device=`echo "$line" | awk '{print $1}'`
        errors=
        echo "mdadm($device).name = 'Mdadm /dev/$device'";
        echo "mdadm($device).expected = 0";
    elif [[ ! $errors ]]; then
        errors=`echo -n "$line" | egrep -o '_' | tr -d '\n' | wc -c`;
        echo "mdadm($device).value = $errors";
    fi
done
