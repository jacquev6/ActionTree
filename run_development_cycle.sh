#!/bin/bash

set -o errexit

# pip2 install --quiet --upgrade --user matplotlib graphviz sphinx coverage mock futures
# pip3 install --quiet --upgrade --user matplotlib graphviz pep8

coverage2 run --include "ActionTree/*" --branch setup.py test --quiet

coverage2 report --show-missing | grep -v "^ActionTree.*100%$"

coverage2 html --directory=build/coverage
echo
echo "See coverage details in $(pwd)/build/coverage/index.html"
echo

python setup.py build_sphinx --quiet --builder=doctest

python3 setup.py test --quiet

pep8 --max-line-length=120 ActionTree setup.py doc

python setup.py build_sphinx
rm -rf docs
cp -r build/sphinx/html docs
touch docs/.nojekyll
echo
echo "See documentation in $(pwd)/docs/index.html"
echo

echo "Development cycle OK"
