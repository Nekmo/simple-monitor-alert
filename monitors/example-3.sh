#!/usr/bin/env bash
echo "file_exists.expected=yes"
echo "file_exists.require_param = yes"
if [ -f "$file_exists" ]; then value="yes"; else value="no"; fi
echo "file_exists.value=$value"


echo "test.expected = yes"
echo "test.value = yes"

echo "test2.expected = yes"
echo "test2.value = yes"
