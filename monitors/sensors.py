#!/usr/bin/env python
# -*- coding: utf-8 -*-

from subprocess import check_output

import re

import sys


class Chip(list):
    def __init__(self, name):
        super(Chip, self).__init__()
        self.name = name


class Sensor(dict):
    measures = [
        {'comp': '>=', 'name': 'min', 'level': 'average'},
        {'comp': '<=', 'name': 'max', 'level': 'average'},
        {'comp': '<=', 'name': 'crit', 'level': 'high'},
    ]
    types = {'temp': 'temperature', 'in': 'voltage', 'fan': 'fan', 'intrusion': 'intrusion'}
    types_symbols = {'temperature': 'ºC', 'voltage': 'V', 'fan': 'RPM'}

    def __init__(self, name):
        name = name.rstrip(':')
        self.name = name
        self._type = None
        super(Sensor, self).__init__()

    def add(self, key, value):
        self[key] = value

    def add_line(self, line):
        line = line.lstrip(' ')
        self._type, line = line.split('_', 1)
        key, value = line.split(': ')
        try:
            value = float(value)
        except ValueError:
            pass
        self.add(key, value)

    def get_type(self):
        type = re.split('\d+', self._type)[0]
        return self.types.get(type)

    def get_type_symbol(self):
        return self.types_symbols.get(self.get_type(), '')

    def get_value(self):
        return self.get('input', None)

    def get_measures(self):
        for data in self.measures:
            expected = self.get(data['name'])
            if expected is None:
                continue
            data = dict(data)
            data['expected'] = expected
            yield data

    def __repr__(self):
        d = dict(self)
        value = d.pop('input', None)
        return '<{} {}{} {}>'.format(self.name, value, self.get_type_symbol(),
                                     ' '.join(map(lambda x: '{}={}'.format(x, self[x]), d)))


def get_sensors():
    chips = []
    chip = None
    sensor = None
    for line in check_output(['sensors', '-u', '--no-adapter']).split(b'\n'):
        line = line.decode(sys.getdefaultencoding())
        line = line.rstrip('\n')
        if not line:
            chip = None
        elif chip is None:
            chip = Chip(line)
            chips.append(chip)
        elif not line.startswith('  '):
            sensor = Sensor(line)
            chip.append(sensor)
        else:
            sensor.add_line(line)
    return chips


def _print_sma_sensor(chip, sensor):
    value = sensor.pop('input', None)
    if not value:
        return
    for measure in sensor.get_measures():
        key = 'sensor_{}({}-{})'.format(measure['name'], chip.name, sensor.name.replace(' ', '-'))
        print('{}.name = "{} sensor {}->{} ({})"'.format(key, sensor.get_type().title(), chip.name,
                                                         sensor.name, measure['name']))
        print('{}.value = {}'.format(key, value))
        print('{}.expected = {} {}'.format(key, measure['comp'], measure['expected']))
        print('{}.level = {}'.format(key, measure['level']))


def sma_sensors():
    for chip in get_sensors():
        for sensor in chip:
            _print_sma_sensor(chip, sensor)

if __name__ == '__main__':
    sma_sensors()
