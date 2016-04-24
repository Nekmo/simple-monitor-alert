#!/usr/bin/env bash
echo "file_exists.expected=yes"
echo "file_exists.require_param = yes"
if [ -f "$file_exists" ]; then value="yes"; else value="no"; fi
echo "file_exists.value=$value"
