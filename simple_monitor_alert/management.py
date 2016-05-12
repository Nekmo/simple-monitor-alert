"""A simple monitor with alerts for Unix
"""


import argparse
import logging

from simple_monitor_alert.sma import SMA, SMAService

SMA_INI_FILE = '/etc/simple-monitor-alert/sma.ini'
MONITORS_DIR = '/etc/simple-monitor-alert/monitors-enabled/'
ALERTS_DIR = '/etc/simple-monitor-alert/alerts/'


def create_logger(name, level=logging.INFO):
    # create logger
    logger = logging.getLogger(name)
    logger.setLevel(level)

    # create console handler and set level to debug
    ch = logging.StreamHandler()
    ch.setLevel(level)

    # create formatter
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)-7s - %(message)s')

    # add formatter to ch
    ch.setFormatter(formatter)

    # add ch to logger
    logger.addHandler(ch)


def execute_from_command_line(argv=None):
    """
    A simple method that runs a ManagementUtility.
    """

    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--monitors-dir', default=MONITORS_DIR)
    parser.add_argument('--alerts-dir', default=ALERTS_DIR)
    parser.add_argument('--config', default=SMA_INI_FILE)

    parser.add_argument('--warning', help='set logging to warning', action='store_const', dest='loglevel',
                        const=logging.WARNING, default=logging.INFO)
    parser.add_argument('--quiet', help='set logging to ERROR', action='store_const', dest='loglevel',
                        const=logging.ERROR, default=logging.INFO)
    parser.add_argument('--debug', help='set logging to DEBUG',
                        action='store_const', dest='loglevel',
                        const=logging.DEBUG, default=logging.INFO)
    parser.add_argument('--verbose', help='set logging to COMM',
                        action='store_const', dest='loglevel',
                        const=5, default=logging.INFO)

    parser.sub = parser.add_subparsers()

    parse_service = parser.sub.add_parser('service', help='Run SMA as service (daemon).')
    parse_service.set_defaults(which='service')

    parse_alerts = parser.sub.add_parser('alerts', help='Alerts options.')
    parse_alerts.set_defaults(which='alerts')
    parse_alerts.add_argument('--test', help = 'Test alert', action='store_true')
    parse_alerts.add_argument('alert_section', nargs='?', help='Alert section to see')


    args = parser.parse_args(argv[1:])

    create_logger('sma', args.loglevel)

    if not getattr(args, 'which', None):
        sma = SMA(args.monitors_dir, args.alerts_dir, args.config)
        sma.evaluate_and_alert()
    elif args.which == 'service':
        sma = SMAService(args.monitors_dir, args.alerts_dir, args.config)
        sma.start()
    elif args.which == 'alerts' and args.test:
        sma = SMA(args.monitors_dir, args.alerts_dir, args.config)
        sma.alerts.test()
