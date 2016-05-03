.. image:: https://img.shields.io/travis/Nekmo/simple-monitor-alert.svg?style=flat-square&maxAge=2592000
  :target: https://travis-ci.org/Nekmo/simple-monitor-alert
  :alt: Latest Travis CI build status

.. image:: https://img.shields.io/pypi/v/simple-monitor-alert.svg?style=flat-square
  :target: https://pypi.python.org/pypi/simple-monitor-alert
  :alt: Latest PyPI version

.. image:: https://img.shields.io/pypi/pyversions/simple-monitor-alert.svg?style=flat-square
  :target: https://pypi.python.org/pypi/simple-monitor-alert
  :alt: Python versions

.. image:: https://img.shields.io/codeclimate/github/Nekmo/simple-monitor-alert.svg?style=flat-square
  :target: https://codeclimate.com/github/Nekmo/simple-monitor-alert
  :alt: Code Climate

.. image:: https://img.shields.io/codecov/c/github/Nekmo/simple-monitor-alert/master.svg?style=flat-square
  :target: https://codecov.io/github/Nekmo/simple-monitor-alert
  :alt: Test coverage

.. image:: https://img.shields.io/requires/github/Nekmo/simple-monitor-alert.svg?style=flat-square
     :target: https://requires.io/github/Nekmo/simple-monitor-alert/requirements/?branch=master
     :alt: Requirements Status


Simple Monitor Alert
####################
A simple monitor with alerts for Unix/Linux under the KISS philosophy. Keep It Simple, Stupid!

- Light: Only ~7MiB of RAM. (That's great for your raspberry pi!)
- Very easy to use and understand.
- Write your own monitors in any language (Bash, Python, Perl, JS, Ruby, PHP, C, C++...).
- Awesome features: send alerts once or several times, graphic peak...
- No server required. You can run as a daemon or using crond.
- Easy to debug and test.
- Multiple ways to send alerts: email, telegram...
- Easy configuration in a single file.

Extra Quick Guide in 3 steps
============================

1. Install it from Pypi::

    sudo pip install simple-monitor-alert

2. Edit `/etc/simple-monitor-alert/sma.ini` and defines the recipient of the alerts::

    [email]
    to = awesome@email.com

3. Execute sma::

    # Just once:
    sma
    # or... Run as a service (daemon)
    sma service
    # or... Run usign system service:
    sudo systemctl start sma

And yes, that's it!
