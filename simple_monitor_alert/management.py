import argparse

from simple_monitor_alert.monitor import Monitors

"""A simple monitor with alerts for Unix
"""

SMA_INI_FILE = '/etc/simple-monitor-alert/sma.ini'
MONITORS_DIR = '/etc/simple-monitor-alert/monitors/'
SETTINGS_DIR = '/etc/simple-monitor-alert/settings/'


def execute_from_command_line(argv=None):
    """
    A simple method that runs a ManagementUtility.
    """

    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--monitors-dir', default=MONITORS_DIR)
    parser.add_argument('--settings-dir', default=SETTINGS_DIR)
    parser.add_argument('--sma-ini-file', default=SMA_INI_FILE)

    args = parser.parse_args(argv[1:])
    monitors = Monitors(args.monitors_dir, args.sma_ini_file, args.settings_dir)
    monitors.execute_all()
