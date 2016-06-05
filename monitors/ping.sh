#!/usr/bin/env bash
# Ping machine monitor.
# Pings a address
# It requires a parameter: address. For example, google.com
# [ping]
# ping.param = google.com
#
# You can monitor multiple destinations:
# [ping]
# ping(google).param = google.com
# ping(htpc).param = 192.168.1.2
#
# Add the configuration to:
# /etc/simple-monitor-alert/sma.ini


if [[ ! $ping ]]; then
    exit
fi
output=$((ping -c 1 -W 4 $ping) 2>&1 1>&1);
code=$?
echo "ping.name ='Ping to $ping'"
echo "ping.value = $code"
echo "ping.expected = 0"
if [[ $code == 1 ]]; then
    echo "ping.extra_info = 'No reply from $ping'";
elif [[ $code != 0 ]]; then
    echo "ping.extra_info = $output";
fi