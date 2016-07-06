#!/usr/bin/env python
# -*- coding: utf-8 -*-
import distutils
import filecmp
import getpass
import shutil
import subprocess

import pwd

import grp
from distutils.version import LooseVersion

from setuptools import setup, find_packages, Command
import pip
from distutils.util import convert_path
from fnmatch import fnmatchcase
import os
import sys
import uuid
from simple_monitor_alert.utils.files import makedirs

if hasattr(pip, '__version__') and LooseVersion(pip.__version__) >= LooseVersion('6.0.0'):
    from pip.req import parse_requirements
else:
    class FakeReq(object):
        link = None

        def __init__(self, req):
            self.req = req

    def parse_requirements(reqs_path, *args, **kwargs):
        return [FakeReq(line.strip()) for line in open(reqs_path).readlines()]


def first_path_exist(paths):
    for test_path in paths:
        if os.path.exists(test_path):
            return test_path

###############################
#  Configuración del paquete  #
###############################

# Instrucciones:
# 1. Rellene la información de esta sección.
# 2. Incluya un archivo requirements.txt con las dependencias.
# 3. Cambie el archivo LICENSE.txt por el de su licencia.
# 4. Añada un archivo README, README.rst o README.md, el cual se trata de la la descripción extendida.

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

#  Información del autor
from setuptools.command.install import install

AUTHOR = 'Nekmo'
EMAIL = 'contacto@nekmo.com'

# Información del paquete
PACKAGE_NAME = 'simple-monitor-alert'
PACKAGE_DOWNLOAD_URL = 'https://github.com/Nekmo/simple-monitor-alert/archive/master.zip'  # .tar.gz
URL = 'https://github.com/Nekmo/simple-monitor-alert'  # Project url
STATUS_LEVEL = 1  # 1:Planning 2:Pre-Alpha 3:Alpha 4:Beta 5:Production/Stable 6:Mature 7:Inactive
KEYWORDS = ['linux', 'unix', 'monitor', 'alert', 'simple-monitor-alert', 'notifications', 'email', 'telegram']
# https://github.com/github/choosealicense.com/tree/gh-pages/_licenses
LICENSE = 'MIT'
CLASSIFIERS = [
    # Common licenses
    'License :: OSI Approved :: MIT License',
    'Topic :: System :: Networking :: Monitoring',
    'Topic :: System :: Networking :: Monitoring :: Hardware Watchdog',
    'Topic :: System :: Monitoring',
    'Operating System :: POSIX :: Linux',
    'Operating System :: POSIX :: BSD',
    'Operating System :: POSIX',
    # 'License :: OSI Approved :: GNU General Public License v3 (GPLv3)',
    # 'License :: OSI Approved :: BSD License',
]  # https://pypi.python.org/pypi?%3Aaction=list_classifiers
NATURAL_LANGUAGE = 'English'  # English...
DESCRIPTION = """\
A simple monitor with alerts for Unix/Linux under the KISS philosophy. Keep It Simple, Stupid!
"""

# Requerido para la correcta instalación del paquete
PLATFORMS = [
    # 'universal',
    'linux',
    # 'macosx',
    # 'solaris',
    # 'irix',
    # 'win'
    # 'bsd'
    # 'ios'
    # 'android'
]
ROOT_INCLUDE = ['requirements.txt', 'VERSION', 'LICENSE.txt']
PYTHON_VERSIONS = ['2.7', '3.3-3.5']  # or ranges: 3.1-3.5, 2.6-3.4...
INSTALL_REQUIRES = []  # Necesario si no hay un requirements.txt

######## FIN DE LA CONFIGURACIÓN DEL PAQUTE ########

__author__ = AUTHOR
__dir__ = os.path.abspath(os.path.dirname(__file__))

# paths
readme_path = os.path.join(__dir__, 'README')
for target in ['README.rst', 'README.md']:
    if not os.path.exists(readme_path):
        readme_path = os.path.join(__dir__, target)

version_path = os.path.join(__dir__, 'VERSION')
requirements_path = os.path.join(__dir__, 'requirements.txt')
scripts_path = os.path.join(__dir__, 'scripts')


def get_url(ir):
    if hasattr(ir, 'url'): return ir.url
    if ir.link is None: return
    return ir.link.url


##############################################################################
# find_package_data is an Ian Bicking creation.

# Provided as an attribute, so you can append to these instead
# of replicating them:
standard_exclude = ('*.py', '*.pyc', '*~', '.*', '*.bak', '*.swp*')
standard_exclude_directories = ('.*', 'CVS', '_darcs', './build',
                                './dist', 'EGG-INFO', '*.egg-info')


def find_package_data(where='.', package='',
                      exclude=standard_exclude,
                      exclude_directories=standard_exclude_directories,
                      only_in_packages=True,
                      show_ignored=False):
    """
    Return a dictionary suitable for use in ``package_data``
    in a distutils ``setup.py`` file.

    The dictionary looks like::

        {'package': [files]}

    Where ``files`` is a list of all the files in that package that
    don't match anything in ``exclude``.

    If ``only_in_packages`` is true, then top-level directories that
    are not packages won't be included (but directories under packages
    will).

    Directories matching any pattern in ``exclude_directories`` will
    be ignored; by default directories with leading ``.``, ``CVS``,
    and ``_darcs`` will be ignored.

    If ``show_ignored`` is true, then all the files that aren't
    included in package data are shown on stderr (for debugging
    purposes).

    Note patterns use wildcards, or can be exact paths (including
    leading ``./``), and all searching is case-insensitive.

    This function is by Ian Bicking.
    """

    out = {}
    stack = [(convert_path(where), '', package, only_in_packages)]
    while stack:
        where, prefix, package, only_in_packages = stack.pop(0)
        for name in os.listdir(where):
            fn = os.path.join(where, name)
            if os.path.isdir(fn):
                bad_name = False
                for pattern in exclude_directories:
                    if (fnmatchcase(name, pattern)
                        or fn.lower() == pattern.lower()):
                        bad_name = True
                        if show_ignored:
                            sys.stderr.write(
                                "Directory %s ignored by pattern %s\n"
                                % (fn, pattern))
                        break
                if bad_name:
                    continue
                if os.path.isfile(os.path.join(fn, '__init__.py')):
                    if not package:
                        new_package = name
                    else:
                        new_package = package + '.' + name
                    stack.append((fn, '', new_package, False))
                else:
                    stack.append(
                        (fn, prefix + name + '/', package, only_in_packages)
                    )
            elif package or not only_in_packages:
                # is a file
                bad_name = False
                for pattern in exclude:
                    if (fnmatchcase(name, pattern)
                        or fn.lower() == pattern.lower()):
                        bad_name = True
                        if show_ignored:
                            sys.stderr.write(
                                "File %s ignored by pattern %s\n"
                                % (fn, pattern))
                        break
                if bad_name:
                    continue
                out.setdefault(package, []).append(prefix + name)
    return out


##############################################################################

# Lista de dependencias a instalar
if os.path.exists(requirements_path):
    requirements = list(parse_requirements(requirements_path, session=uuid.uuid1()))
    install_requires = [str(ir.req) for ir in requirements]
    dependency_links = [get_url(ir) for ir in requirements if get_url(ir)]
else:
    install_requires = INSTALL_REQUIRES
    dependency_links = []

# Todos los módulos y submódulos a instalar (module, module.submodule, module.submodule2...)
packages = find_packages(__dir__)
# Prevent include symbolic links
for package in tuple(packages):
    path = os.path.join(__dir__, package.replace('.', '/'))
    if not os.path.exists(path):
        continue
    if not os.path.islink(path):
        continue
    packages.remove(package)

# Otros archivos que no son Python y que son requeridos
package_data = {'': ROOT_INCLUDE}

# Obtener la lista de módulos que se instalarán
modules = list(filter(lambda x: '.' not in x, packages))

for module in modules:
    package_data.update(find_package_data(
        module,
        package=module,
        only_in_packages=False,
    ))

# Descripción larga si existe un archivo README
try:
    long_description = open(readme_path, 'rt').read()
except IOError:
    long_description = ''

# Tomar por defecto la versión de un archivo VERSION. Si no, del módulo
if os.path.exists(version_path):
    package_version = open(version_path).read().replace('\n', '')
else:
    package_version = __import__(modules[0]).__version__

# Si hay un directorio scripts, tomar todos sus archivos
if os.path.exists(scripts_path):
    scripts_dir_name = scripts_path.replace(__dir__, '', 1)
    scripts_dir_name = scripts_dir_name[1:] if scripts_dir_name.startswith(os.sep) else scripts_dir_name
    scripts = [os.path.join(scripts_dir_name, file) for file in os.listdir(scripts_path)]
else:
    scripts = []

# Eliminar archivos de ROOT_INCLUDE que no existen
for d in tuple(ROOT_INCLUDE):
    if not os.path.exists(os.path.join(__dir__, d)):
        ROOT_INCLUDE.remove(d)

# Nombre del estado de desarrollo
status_name = ['Planning', 'Pre-Alpha', 'Alpha', 'Beta',
               'Production/Stable', 'Mature', 'Inactive'][STATUS_LEVEL - 1]

# Añadir en los classifiers la plataforma
platforms_classifiers = {'linux': ('POSIX', 'Linux'), 'win': ('Microsoft', 'Windows'),
                         'solaris': ('POSIX', 'SunOS/Solaris'), 'aix': ('POSIX', 'Linux'), 'unix': ('Unix',),
                         'bsd': ('POSIX', 'BSD')}
for key, parts in platforms_classifiers.items():
    if not key in PLATFORMS:
        continue
    CLASSIFIERS.append('Operating System :: {0}'.format(' :: '.join(parts)))


# Añadir la versión de Python a los Classifiers
def frange(x, y, jump):
    while x < y:
        yield x
        x += jump


python_versions = []
for version in PYTHON_VERSIONS:
    if '-' in version:
        version = version.split('-')
        if len(version) != 2:
            raise ValueError('Invalid Python version range: {0}'.format('-'.join(version)))
        version = list(map(float, version))
        version[1] += 0.1  # Para que frange incluya la última versión
        python_versions.extend(frange(version[0], version[1], 0.1))
    elif isinstance(version, int) or version.isdigit():
        python_versions.append(str(version))
    else:
        python_versions.append(float(version))
python_versions = map(lambda x: x if isinstance(x, str) else '%.1f' % x, python_versions)
# Eliminar versiones 0-2.3 y 2.8-2.9
remove_python_versions = map(str, list(frange(0, 2.3, 0.1)) + list(frange(2.8, 3.0, 0.1)))
python_versions = list(filter(lambda x: x not in remove_python_versions, python_versions))
for version in range(2, 4):
    if not len(list(filter(lambda x: int(float(x)) != version, python_versions))):
        # Sólo se encuentran versiones para la versión <version>
        python_versions.append('%i :: Only' % version)
        break
CLASSIFIERS.extend(['Programming Language :: Python :: %s' % version for version in python_versions])
CLASSIFIERS.extend([
    'Natural Language :: {0}'.format(NATURAL_LANGUAGE),
    'Development Status :: {0} - {1}'.format(STATUS_LEVEL, status_name),
])


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


class SystemInstallCommand(install):
    """Custom install setup to help run shell commands (outside shell) before installation"""

    def run(self):
        print('Starting Python module installation.')
        self.do_egg_install()
        print('-' * 80)
        if getpass.getuser() != 'root':
            print('WARNING: Simple-Monitor-Alert installed as "{}". Install as root to create the system files!')
            return
        print('Installing things that are not Python (system files).')
        for directory in [ENABLED_MONITORS_DIR, os.path.dirname(AVAILABLE_MONITORS_DIR)]:
            print('Creating directory {}'.format(directory))
            makedirs(directory, exist_ok=True)
        dir_path = os.path.dirname(os.path.realpath(__file__))
        for src_name, dest in [('monitors', MONITORS_DIR), ('alerts', ALERTS_DIR)]:
            print('Copying directory "{}" to "{}"'.format(os.path.join(dir_path, src_name), dest))
            distutils.dir_util.copy_tree(os.path.join(dir_path, src_name), dest)
        for from_, to in [(MONITORS_DIR, AVAILABLE_MONITORS_DIR), (ALERTS_DIR, AVAILABLE_ALERTS_DIR)]:
            if not os.path.exists(to):
                print('Creating symbolic link "{}" -> "{}"'.format(from_, to))
                os.symlink(from_, to)
        if not os.listdir(ENABLED_MONITORS_DIR):
            print('Enabling defaults monitors: {}'.format(', '.join(DEFAULT_ENABLEDS_MONITORS)))
            for enabled_monitor in DEFAULT_ENABLEDS_MONITORS:
                os.symlink('../{}/{}'.format(os.path.split(AVAILABLE_MONITORS_DIR)[1], enabled_monitor),
                           os.path.join(ENABLED_MONITORS_DIR, enabled_monitor))
        print('Creating user {}'.format(USERNAME))
        p = subprocess.Popen(['useradd', USERNAME])
        if sys.version_info >= (3,3):
            p.wait(2)
        else:
            p.wait()
        if p.returncode not in [0, 9]:
            raise Exception('It has failed to create the user {}. Returncode: {}'.format(USERNAME, p.returncode))
        print('Creating variable data directory: {}'.format(VAR_DIRECTORY))
        makedirs(VAR_DIRECTORY, 0o700, True)
        uid = pwd.getpwnam(USERNAME).pw_uid
        gid = grp.getgrnam("root").gr_gid
        os.chown(VAR_DIRECTORY, uid, gid)
        print('Copying services')
        for src, dest in SERVICES:
            if not os.path.lexists(os.path.dirname(dest)):
                continue
            if os.path.exists(dest) and filecmp.cmp(os.path.join(dir_path, src), dest):
                continue
            create_backup(dest)
            shutil.copy(os.path.join(dir_path, src), dest)
        print('Copying sma template file')
        if not os.path.lexists(SMA_FILE):
            shutil.copy(os.path.join(dir_path, SMA_TEMPLATE_FILENAME), SMA_FILE)


class FakeBdistWheel(Command):
    description = 'Faked Wheel'
    user_options = []

    def initialize_options(self):
        pass

    def finalize_options(self):
        pass

    def run(self):
        print('Sorry, but wheel is not supported for this package!')


# http://thomas-cokelaer.info/blog/2012/03/how-to-embedded-data-files-in-python-using-setuptools/
def get_datafiles(datadirs):
    for datadir in datadirs:
        for d, folders, files in os.walk(datadir):
            yield (d, [os.path.join(d, f) for f in files if not f.endswith('.pyc')])


setup(
    cmdclass={'install': SystemInstallCommand, 'bdist_wheel': FakeBdistWheel},

    name=PACKAGE_NAME,
    version=package_version,

    description=DESCRIPTION,
    long_description=long_description,

    author=AUTHOR,
    author_email=EMAIL,

    url=URL,

    license=LICENSE,
    classifiers=CLASSIFIERS,

    platforms=PLATFORMS,

    provides=modules,
    install_requires=install_requires,
    dependency_links=dependency_links,

    packages=packages,
    include_package_data=True,
    # Scan the input for package information
    # to grab any data files (text, images, etc.)
    # associated with sub-packages.
    package_data=package_data,

    download_url=PACKAGE_DOWNLOAD_URL,
    keywords=KEYWORDS,
    scripts=scripts,
    data_files=get_datafiles(['monitors', 'alerts', 'services']),


    # entry_points={},

    zip_safe=False,
)
