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

3-Step Quick Start Guide
========================

1. Install it from Pypi::

    sudo pip install simple-monitor-alert

2. Edit `/etc/simple-monitor-alert/sma.ini` and defines the recipient of the alerts::

    [mail]
    to = awesome@email.com

3. Execute sma::

    # Just once:
    sma
    # or... Run as a service (daemon)
    sma service
    # or... Run usign system service:
    sudo systemctl start sma

And yes, that's it!

5 minutes guide
===============

Files and directories:

  - `/etc/simple-monitor-alert/sma.ini` (file): all-in-one config file. Configure monitors and alerts methods.
  - `/etc/simple-monitor-alert/monitors-available` (directory): All monitors available for usage. You can create
  monitors here.
  - `/etc/simple-monitor-alert/monitors-enabled` (directory): All monitors that are here are activated.
  - `/etc/simple-monitor-alert/alerts` (directory): Alerts methods available. You need to configure them in sma.ini.


Enable and disable monitors
---------------------------
All monitors in `/etc/simple-monitor-alert/monitors-enabled` are enabled. It is recommended that files are symbolic
links. To **activate** a monitor::

  $ cd /etc/simple-monitor-alert/monitors-enabled
  $ sudo ln -s ../monitors-available/mdadm.sh

To **disable**::

  $ cd /etc/simple-monitor-alert/monitors-enabled
  $ rm mdadm.sh # It's safe. mdadm is a symlink.

We recommend you read the beginning of the monitor before activating. Some monitors may require parameters and
configure the system. For example::

  $ head -n 6 /etc/simple-monitor-alert/monitors-available/service.sh
  #!/usr/bin/env bash
  # Service Status monitor.
  # Verify that the service is running.
  # It requires a parameter: service name. For example, sshd.
  # [service]
  # service_status.param = sshd


To pass the parameter you must add the following to `sma.ini`::

  [service]
  service_status.param = sshd

To monitor multiple services::

  [service]
  service_status(sshd).param = sshd
  service_status(ntpd).param = ntpd


Debugging
---------
You can test your monitors running them::

  $ /etc/simple-monitor-alert/monitors-available/mdadm.sh
  mdadm(md0).name = 'Mdadm /dev/md0'
  mdadm(md0).expected = 0
  mdadm(md0).value = 0

You can also run sma and see the results::

  $ sma
  2016-05-03 00:28:14,972 - sma - INFO    - Trigger: [success] (mdadm) mdadm(md0). Result: 0 == 0
  2016-05-03 00:28:14,990 - sma - INFO    - Trigger: [success] (system) ram. Result: 32.1427 <= 85
  2016-05-03 00:28:14,990 - sma - INFO    - Trigger: [success] (system) cpu. Result: 9.57627 <= 80
  2016-05-03 00:28:15,156 - sma - WARNING - Trigger: [warning] (hdds) pcnt_use(sdc1). Assertion 98 <= 80 failed.
  Extra info: Space: 23G/25G
  2016-05-03 00:28:15,157 - sma - WARNING - Trigger: [warning] (hdds) pcnt_use(md0). Assertion 100 <= 80 failed.
  Extra info: Space: 5,4T/5,5T

To test the alerts you can use::

  $ sma alerts --test


My first monitor
----------------
SMA works by checking the output of your monitor script. A monitor has observables. Each observable has 2 major
sections: the expected value and the value obtained::

  observable1.expected = yes
  observable1.value = yes
  observable2.expected = yes
  observable2.value = no

In this example the first observable is fine and the second is under error. Your program should return something
similar. The following example check that a file exists::

  #!/usr/bin/env bash
  echo "file_exists.expected = yes"
  if [ -f "/path/to/file" ]; then value="yes"; else value="no"; fi
  echo "file_exists.value = $value"

Output::

  $ /etc/simple-monitor-alert/monitors-available/example-1.sh
  file_exists.expected = yes
  file_exists.value = no

There are more options with monitors, such as obtaining arguments. For more information see the documentation.