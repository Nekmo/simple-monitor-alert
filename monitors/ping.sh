#!/usr/bin/env bash

output=$((ping -c 1 -W 4 $ping) 2>&1);
code=$?
echo "ping.name ='Ping to $ping'"
echo "ping.value = $code"
echo "ping.expected = 0"
if [[ $code == 1 ]]; then
    echo "ping.extra_info = 'No reply from $ping'";
elif [[ $code ]]; then
    echo "ping.extra_info = $output";
fi