#!/bin/bash

# Copyright 2017-2018 Vincent Jacques <vincent@vincent-jacques.net>

# GENI: prologue
# GENERATED SECTION, MANUAL EDITS WILL BE LOST
set -o errexit -o pipefail
IFS=$'\n\t'

PROJECT_ROOT=$(pwd)

SHOW_IN_BROWSER=false
function show_in_browser {
  echo
  echo "$1: $PROJECT_ROOT/$2"
  echo
  if $SHOW_IN_BROWSER
  then
    python -m webbrowser -t file://$PROJECT_ROOT/$2
  fi
}

DO_DOC=true
DO_DOCTESTS=true
DO_PIP_INSTALL=true

while [[ "$#" > 0 ]]
do
  case $1 in
    -wb|--web-browser)
      SHOW_IN_BROWSER=true
      ;;
    --skip-doc)
      DO_DOC=false
      ;;
    --skip-doctests)
      DO_DOCTESTS=false
      ;;
    --skip-pip-install)
      DO_PIP_INSTALL=false
      ;;
    -q|--quick)
      DO_DOC=false
      DO_DOCTESTS=false
      DO_PIP_INSTALL=false
      ;;
    *)
      echo "Unknown parameter passed: $1"
      exit 1;;
  esac
  shift
done
# END OF GENERATED SECTION


# GENI: install_dependencies
# GENERATED SECTION, MANUAL EDITS WILL BE LOST
if ! [ -d _builds/venv2.dev_with_oldest_versions ]; then virtualenv --always-copy --python=python2 _builds/venv2.dev_with_oldest_versions; fi
. _builds/venv2.dev_with_oldest_versions/bin/activate
pip install --upgrade pip setuptools wheel coverage sphinx
pip install --upgrade graphviz matplotlib mock
deactivate

if ! [ -d _builds/venv3.dev_with_newest_versions ]; then virtualenv --always-copy --python=python3 _builds/venv3.dev_with_newest_versions; fi
. _builds/venv3.dev_with_newest_versions/bin/activate
pip install --upgrade pip setuptools wheel coverage sphinx
pip install --upgrade graphviz matplotlib mock
deactivate
# END OF GENERATED SECTION


# GENI: run_tests
# GENERATED SECTION, MANUAL EDITS WILL BE LOST
. _builds/venv2.dev_with_oldest_versions/bin/activate
coverage erase
coverage run --branch --include="ActionTree*" setup.py test --quiet
coverage combine
coverage report
echo
coverage html --directory=_builds/coverage_with_oldest_versions
show_in_browser "Coverage details (with oldest versions)" _builds/coverage_with_oldest_versions/index.html
coverage erase
if $DO_DOCTESTS; then python setup.py build_sphinx --builder=doctest; fi
deactivate

. _builds/venv3.dev_with_newest_versions/bin/activate
coverage erase
coverage run --branch --include="build/lib/ActionTree*" setup.py test --quiet
coverage combine
coverage report
echo
coverage html --directory=_builds/coverage_with_newest_versions
show_in_browser "Coverage details (with newest versions)" _builds/coverage_with_newest_versions/index.html
coverage erase
deactivate
# END OF GENERATED SECTION


# GENI: check_code
# GENERATED SECTION, MANUAL EDITS WILL BE LOST
python3 setup.py check --strict --metadata --restructuredtext
pycodestyle --max-line-length=120 $(git ls-files "*.py")
# END OF GENERATED SECTION


# GENI: documentation
# GENERATED SECTION, MANUAL EDITS WILL BE LOST
if $DO_DOC
then
  . _builds/venv3.dev_with_newest_versions/bin/activate
  python setup.py build_sphinx
  deactivate
  rm -rf docs
  cp -r build/sphinx/html docs
  show_in_browser "Documentation" docs/index.html
fi
# END OF GENERATED SECTION


# GENI: install
# GENERATED SECTION, MANUAL EDITS WILL BE LOST
if $DO_PIP_INSTALL
then
  rm -rf _builds/venv2.install
  virtualenv --always-copy --python=python2 _builds/venv2.install
  . _builds/venv2.install/bin/activate
  pip install .
  deactivate

  rm -rf _builds/venv3.install
  virtualenv --always-copy --python=python3 _builds/venv3.install
  . _builds/venv3.install/bin/activate
  pip install .
  deactivate
fi
# END OF GENERATED SECTION


# cd demo
# ./demo.py


# GENI: epilogue
# GENERATED SECTION, MANUAL EDITS WILL BE LOST
echo
echo "Development cycle OK"
# END OF GENERATED SECTION
