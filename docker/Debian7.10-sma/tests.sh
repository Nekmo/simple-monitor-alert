#!/usr/bin/env bash
pip install git+https://github.com/Nekmo/simple-monitor-alert.git@v0.2.3#egg=simple-monitor-alert
ls /etc/simple-monitor-alert/sma.ini
ls /etc/init.d/sma.sh
/etc/init.d/sma.sh start
sudo -u sma sma