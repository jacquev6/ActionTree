#!/bin/bash

set -o errexit

clear

git checkout docs


# ./develop.py dependencies


./develop.py test


pep8 --max-line-length=120 ActionTree *.py doc/conf.py


python setup.py build_sphinx
rm -rf docs
cp -r build/sphinx/html docs
touch docs/.nojekyll
rm -f docs/.buildinfo
echo
echo "See documentation in $(pwd)/docs/index.html"
echo


# python3 setup.py install
# cd demo
# ./demo.py


echo "Development cycle OK"
