#!/bin/bash

set -o errexit

clear

git checkout docs

# pip2 install --quiet --upgrade --user matplotlib graphviz sphinx coverage mock
# pip3 install --quiet --upgrade --user matplotlib graphviz pep8

coverage2 run setup.py test --quiet

coverage2 combine

coverage2 report --show-missing | grep -v "^ActionTree.*100%$"

coverage2 html --directory=build/coverage
echo
echo "See coverage details in $(pwd)/build/coverage/index.html"
echo

python setup.py build_sphinx --builder=doctest

python3 setup.py test --quiet

pep8 --max-line-length=120 ActionTree setup.py doc/conf.py

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
