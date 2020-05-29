#!/bin/bash

set -o errexit


pip install .[all]

python demo/demo.py

echo
echo "Install and demo OK"
