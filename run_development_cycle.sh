#!/bin/bash

# Copyright 2017-2018 Vincent Jacques <vincent@vincent-jacques.net>

set -o errexit

clear

coverage2 erase
coverage2 run --include=ActionTree* setup.py test --quiet
coverage2 combine
coverage2 report

coverage3 erase
coverage3 run --include=build/lib/ActionTree* setup.py test --quiet
coverage3 combine
coverage3 report

python2 setup.py build_sphinx --builder=doctest

python2 setup.py check --strict --metadata --restructuredtext

pycodestyle --max-line-length=120 ActionTree *.py doc/conf.py

python2 setup.py build_sphinx
rm -rf docs
cp -r build/sphinx/html docs
echo
echo "See documentation in $(pwd)/docs/index.html"
echo

# python3 setup.py install
# cd demo
# ./demo.py

echo "Development cycle OK"
