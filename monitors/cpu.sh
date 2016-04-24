#!/usr/bin/env bash
echo "cpu_pcnt.name = 'CPU percentage usage'"
echo "cpu_pcnt.expected= <= 80"
echo "cpu_pcnt.seconds = 600"
echo "cpu_pcnt.value = "`grep 'cpu ' /proc/stat | awk '{ print ($2+$4)*100/($2+$4+$5)}'`