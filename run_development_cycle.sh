#!/bin/bash

set -o errexit

clear

git checkout docs


# pip2 install --quiet --upgrade --user matplotlib graphviz sphinx coverage mock
# pip3 install --quiet --upgrade --user matplotlib graphviz pep8


(
  echo "[run]"
  echo "branch = True"
  echo "include = ActionTree/*"
  echo "concurrency = multiprocessing"
  echo "[report]"
  echo "exclude_lines ="
  echo "  Not unittested: ..."
) > .coveragerc

coverage2 erase

coverage2 run setup.py test --quiet

coverage2 combine

coverage2 report --show-missing | grep -v "^ActionTree.*100%$"

coverage2 html --directory=build/py2_unittest_coverage
echo
echo "See Python 2 unit tests coverage details in $(pwd)/build/py2_unittest_coverage/index.html"
echo

rm .coveragerc


(
  echo "[run]"
  echo "concurrency = multiprocessing"
  echo "[report]"
  echo "exclude_lines ="
  echo "  Not in user guide"
) > .coveragerc

coverage2 erase

coverage2 run setup.py build_sphinx --builder=doctest

mv doc/user_guide/artifacts/.coverage.* .
coverage2 combine

coverage2 report --include="ActionTree/*"

coverage2 html --include="ActionTree/*" --directory=build/py2_doctest_coverage
echo
echo "See Python 2 doc tests coverage details in $(pwd)/build/py2_doctest_coverage/index.html"
echo

rm .coveragerc


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
