#!/bin/bash

set -o errexit


python setup.py check --strict --metadata --restructuredtext

pycodestyle --max-line-length=120 setup.py ActionTree
