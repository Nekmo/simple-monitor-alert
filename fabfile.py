import os
import uuid

import fabric.network
from fabric.api import *

try:
    from secrets import deploy
except ImportError:
    deploy = None


PACKAGE = 'simple-monitor-alert'
env.hosts = getattr(deploy, 'hosts', [])
remote_tmp_dir = os.path.join('/tmp', uuid.uuid4().hex)

archlinux_aur_packages = ['python-humanize', 'python-colorclass-git', 'python-terminaltables', PACKAGE]


def _remove_tmp_dir():
    run('rm -rf {}'.format(remote_tmp_dir))


def _build_aur_package(package):
    with cd(remote_tmp_dir):
        run('git clone https://aur.archlinux.org/{}.git'.format(package))
    tmp_build_dir = os.path.join(remote_tmp_dir, package)
    with cd(tmp_build_dir):
        run('gpg-connect-agent reloadagent /bye')
        run('makepkg --sign')
        pkgs = run('ls -1 *.pkg.tar.xz').splitlines()
    if not pkgs:
        raise Exception('The package {} could not be compiled.'.format(package))
    return os.path.join(tmp_build_dir, pkgs[0].strip('\n'))


def arch_repo():
    run('mkdir -p {}'.format(remote_tmp_dir))
    package_dir = os.path.join(remote_tmp_dir, 'git-'.format(PACKAGE))
    run('mkdir -p {}'.format(package_dir))
    with cd(package_dir):
        run('git clone git+ssh://aur@aur.archlinux.org/{}.git .'.format(PACKAGE))
        put('packages/archlinux/PKGBUILD', package_dir)
        put('packages/archlinux/*.install', package_dir)
        run('makepkg --printsrcinfo > .SRCINFO')
        run('git add .SRCINFO')
        run('git add PKGBUILD')
        run('git add *.install')
        with settings(warn_only=True):
            result = run('git commit -m "Auto: Updated"')
        if result.return_code == 0:
            run('git push')
    for package in archlinux_aur_packages:
        pkg = _build_aur_package(package)
        run('mv {} {}'.format(pkg, deploy.archlinux_repo_dir))
        run('mv {}.sig {}'.format(pkg, deploy.archlinux_repo_dir))
    with cd(deploy.archlinux_repo_dir):
        run('repo-add --sign repo.db.tar.gz *.pkg.tar.xz')
    _remove_tmp_dir()
