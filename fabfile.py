import os
import uuid

import fabric.network
from fabric.api import *

try:
    from secrets import deploy
except ImportError:
    deploy = None


env.hosts = getattr(deploy, 'hosts', [])
remote_tmp_dir = os.path.join('/tmp', uuid.uuid4().hex)

archlinux_aur_packages = ['python-colorclass-git', 'python-humanize', 'python-terminaltables']


def _remove_tmp_dir():
    run('rm -rf {}'.format(remote_tmp_dir))


def _build_aur_package(package):
    with cd(remote_tmp_dir):
        run('git clone https://aur.archlinux.org/{}.git'.format(package))
    tmp_build_dir = os.path.join(remote_tmp_dir, package)
    with cd(tmp_build_dir):
        run('makepkg')
        pkgs = run('ls -1 *.pkg.tar.xz').splitlines()
    if not pkgs:
        raise Exception('The package {} could not be compiled.'.format(package))
    return os.path.join(tmp_build_dir, pkgs[0].strip('\n'))


def arch_repo():
    run('mkdir -p {}'.format(remote_tmp_dir))
    for package in archlinux_aur_packages:
        pkg = _build_aur_package(package)
        run('mv {} {}'.format(pkg, deploy.archlinux_repo_dir))
    with cd(deploy.archlinux_repo_dir):
        run('repo-add repo.db.tar.gz *.pkg.tar.xz')
    _remove_tmp_dir()
