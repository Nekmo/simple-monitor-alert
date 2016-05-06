#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Test your websites.
The following observables are available:

- load_time: Check the load time of your page.
- response_code: Check response code of your page.
- content: The page must contain a given string.

You must define each parameter with:
- method (required).
- url (required).
- headers. [json dict structure]
- request body. [string quoted]

Also, if you use "content" you must add at the end:
- Expected string.

Example:

[web]
; default: 4 seconds
load_time.expected = <= 3
load_time.param = POST http://nekmo.com {"Accept": "text/plain"} "Request content"
; default: 200
response_code.expected = 201
load_time.param = GET https://nekmo.com/subpage
content.param = GET https://nekmo.com/api/ "It requires authentication"
"""
import os
import shlex
import json

import time
from requests.api import request


def parse_dict_param(param):
    start = None
    escaped = False
    for i, char in enumerate(param):
        if escaped:
            escaped = False
            continue
        elif char == '\\':
            escaped = True
        elif char == '{':
            start = i
        elif char == '}':
            return param[start:i+1], param[i+1:]


def parse_param(param):
    groups = param.split(' ', 2)
    headers = {}
    rest = []
    if len(groups) > 2:
        rest = groups[2]
        headers, rest = parse_dict_param(rest)
        headers = json.loads(headers)
        rest = shlex.split(rest)
    result = [groups[0], groups[1], headers]
    result += rest
    return result


def make_request(method, url, headers=None, body=None):
    return request(method.lower(), url, headers=None, data=body)


def test_load_time(*args, **kwargs):
    t = time.time()
    make_request(*args, **kwargs)
    return time.time() - t


def test_response_code(*args, **kwargs):
    req = make_request(*args, **kwargs)
    return req.status_code


def test_content(*args):
    args = list(args)
    expected = args.pop(-1)
    return expected in make_request(*args).text


def _sma_observable(observable_name, expected, function=None, param=None, value=None):
    param = param or os.environ.get(observable_name)
    if not param:
        return
    groups = parse_param(param) if not isinstance(param, list) else param
    function = function or globals()['test_' + observable_name]
    value = value or function(*groups)
    name = function.__name__.replace('test_', '').replace('_', ' ').capitalize()
    print('{}.name = "{} {}"'.format(observable_name, name, groups[1]))
    print('{}.value = {}'.format(observable_name, value))
    print('{}.expected = {}'.format(observable_name, expected))


def sma_web():
    print('X-Timeout: 15')
    _sma_observable('load_time', '<= 4')
    _sma_observable('response_code', 200)
    content_param = os.environ.get('content')
    if content_param:
        content_param = parse_param(content_param)
        value = test_content(*content_param)
        _sma_observable('content', 200, param=content_param, value=value)

if __name__ == '__main__':
    sma_web()