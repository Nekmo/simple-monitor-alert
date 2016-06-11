"""Install script
"""
from __future__ import print_function
import distutils
import filecmp
import grp
import os
import pwd
import shutil
import subprocess
import sys

from simple_monitor_alert.utils.files import makedirs


def first_path_exist(paths):
    for test_path in paths:
        if os.path.exists(test_path):
            return test_path

ENABLED_MONITORS_DIR = '/etc/simple-monitor-alert/monitors-enabled'
AVAILABLE_MONITORS_DIR = '/etc/simple-monitor-alert/monitors-available'
MONITORS_DIR = '/usr/lib/simple-monitor-alert/monitors'
ALERTS_DIR = '/usr/lib/simple-monitor-alert/alerts'
AVAILABLE_ALERTS_DIR = '/etc/simple-monitor-alert/alerts'
SMA_TEMPLATE_FILENAME = 'sma-template.ini'
SMA_FILE = '/etc/simple-monitor-alert/sma.ini'
DEFAULT_ENABLEDS_MONITORS = ['hdds.sh', 'system.sh']
USERNAME = 'sma'
VAR_DIRECTORY = '/var/lib/simple-monitor-alert'
SERVICES = [
    (
        'services/sma.service',
        '{}/sma.service'.format(first_path_exist(['/usr/lib/systemd/system', '/lib/systemd/system']))
    ),
    (
        'services/sma.sh',
        '/etc/init.d/sma.sh'
    )
]


def get_dir_path():
    import simple_monitor_alert
    return os.path.dirname(simple_monitor_alert.__path__[0])


def create_backup(file):
    if not os.path.lexists(file):
        return
    backup_file = file + '.bak'
    i = 0
    while os.path.lexists(backup_file):
        new_backup_file = '{}{}'.format(backup_file, i)
        if not os.path.lexists(new_backup_file):
            backup_file = new_backup_file
            break
        i += 1
    shutil.move(file, backup_file)


def enable_default_monitors(echo=None):
    echo = echo or (lambda x: x)
    if not os.listdir(ENABLED_MONITORS_DIR):
        echo('Enabling defaults monitors: {}'.format(', '.join(DEFAULT_ENABLEDS_MONITORS)))
        for enabled_monitor in DEFAULT_ENABLEDS_MONITORS:
            os.symlink('../{}/{}'.format(os.path.split(AVAILABLE_MONITORS_DIR)[1], enabled_monitor),
                       os.path.join(ENABLED_MONITORS_DIR, enabled_monitor))


def create_symlinks(echo=None):
    echo = echo or (lambda x: x)
    for from_, to in [(MONITORS_DIR, AVAILABLE_MONITORS_DIR), (ALERTS_DIR, AVAILABLE_ALERTS_DIR)]:
        if not os.path.exists(to):
            echo('Creating symbolic link "{}" -> "{}"'.format(from_, to))
            os.symlink(from_, to)


def copy_files(dir_path=None, echo=None):
    dir_path = dir_path or get_dir_path()
    echo = echo or print
    for src_name, dest in [('monitors', MONITORS_DIR), ('alerts', ALERTS_DIR)]:
        echo('Copying directory "{}" to "{}"'.format(os.path.join(dir_path, src_name), dest))
        distutils.dir_util.copy_tree(os.path.join(dir_path, src_name), dest)


def config_directories(echo=None):
    echo = echo or print
    for directory in [ENABLED_MONITORS_DIR, os.path.dirname(AVAILABLE_MONITORS_DIR)]:
        echo('Creating directory {}'.format(directory))
        makedirs(directory, exist_ok=True)


def create_user_group(echo=None):
    echo = echo or (lambda x: x)
    echo('Creating user {}'.format(USERNAME))
    p = subprocess.Popen(['useradd', USERNAME])
    if sys.version_info >= (3, 3):
        p.wait(2)
    else:
        p.wait()
    if p.returncode not in [0, 9]:
        raise Exception('It has failed to create the user {}. Returncode: {}'.format(USERNAME, p.returncode))


def copy_sma(dir_path=None, echo=None):
    dir_path = dir_path or get_dir_path()
    echo = echo or (lambda x: x)
    if not os.path.lexists(SMA_FILE):
        echo('Copying sma template file')
        shutil.copy(os.path.join(dir_path, SMA_TEMPLATE_FILENAME), SMA_FILE)
    else:
        echo('sma file already exists. It has not been updated.')


def create_services(dir_path=None, echo=None):
    dir_path = dir_path or get_dir_path()
    echo = echo or (lambda x: x)
    for src, dest in SERVICES:
        if not os.path.lexists(os.path.dirname(dest)):
            continue
        if os.path.exists(dest) and filecmp.cmp(os.path.join(dir_path, src), dest):
            continue
        create_backup(dest)
        echo('Creating service: {}'.format(dest))
        shutil.copy(os.path.join(dir_path, src), dest)


def var_directory(echo=None):
    echo = echo or (lambda x: x)
    echo('Creating var directory')
    makedirs(VAR_DIRECTORY, 0o700, True)
    uid = pwd.getpwnam(USERNAME).pw_uid
    gid = grp.getgrnam("root").gr_gid
    os.chown(VAR_DIRECTORY, uid, gid)


def install_all(dir_path=None, echo=None):
    dir_path = dir_path or get_dir_path()
    echo = echo or print
    echo('Installing things that are not Python (system files).')
    config_directories(echo)
    copy_files(dir_path, echo)
    create_symlinks(echo)
    enable_default_monitors(echo)
    create_user_group(echo)
    var_directory(echo)
    create_services(dir_path, echo)
    copy_sma(dir_path, echo)


if __name__ == '__main__':
    import argparse
    from simple_monitor_alert.management import set_default_subparser
    argparse.ArgumentParser.set_default_subparser = set_default_subparser
    parser = argparse.ArgumentParser(description=__doc__)
    parser.sub = parser.add_subparsers()
    for option in [enable_default_monitors, create_symlinks, copy_files, config_directories, create_user_group,
                   copy_sma, create_services, var_directory, install_all]:
        option_name = option.__name__
        parse_service = parser.sub.add_parser(option_name.replace('_', '-'),
                                              help='Execute {} function'.format(option_name))
        parse_service.set_defaults(func=option)
    parser.set_default_subparser('install-all')
    args = parser.parse_args()
    args.func()
