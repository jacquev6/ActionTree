#!/bin/bash

set -o errexit

clear

git checkout docs

python2 setup.py test --quiet

python3 setup.py test --quiet

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
