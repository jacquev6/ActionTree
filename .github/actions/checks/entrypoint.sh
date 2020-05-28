#!/bin/bash

set -o errexit


pip install docutils pycodestyle

python setup.py check --strict --metadata --restructuredtext

pycodestyle --max-line-length=120 .
