#!/bin/bash

set -e
set -x

wget https://raw.githubusercontent.com/pypa/pip/master/contrib/get-pip.py -O get-pip.py
{ echo "---------------------------------------------------"; } 2>/dev/null
sha256sum get-pip.py
{ echo "---------------------------------------------------"; } 2>/dev/null
rm get-pip.py

wget https://bootstrap.pypa.io/get-pip.py -O get-pip.py
{ echo "---------------------------------------------------"; } 2>/dev/null
sha256sum get-pip.py
{ echo "---------------------------------------------------"; } 2>/dev/null
rm get-pip.py