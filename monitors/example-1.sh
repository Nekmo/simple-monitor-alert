#!/usr/bin/env bash
echo "file_exists.expected=yes"
if [ -f "/path/to/file" ]; then value="yes"; else value="no"; fi
echo "file_exists.value=$value"
