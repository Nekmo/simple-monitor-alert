#!/usr/bin/env bash
# System monitor. Includes:
# - CPU
# - RAM
# - SWAP
# No arguments required.
echo "cpu.name = 'CPU percentage usage'"
echo "cpu.expected= <= 80"
echo "cpu.seconds = 500"
echo "cpu.value = "`grep 'cpu ' /proc/stat | awk '{ print ($2+$4)*100/($2+$4+$5)}'`

echo "ram.name = 'RAM memory usage'"
echo "ram.expected= <= 85"
echo "ram.seconds = 120"
echo "ram.value = "`free | grep Mem | awk '{print $3/$2 * 100.0}'`

if [[ `free | grep Swap | awk '{print $2}'` != '0' ]]; then
    echo "swap.name = 'SWAP memory usage'"
    echo "swap.expected= <= 80"
    echo "swap.seconds = 120"
    echo "swap.value = "`free | grep Swap | awk '{print $3/$2 * 100.0}'`
fi

