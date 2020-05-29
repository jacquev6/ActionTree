#!/bin/bash

set -o errexit

# @todo Build docs

function title {
  echo $1
  echo $1 | sed s/./=/g
}

title "Checks"
./development/checks/run.sh
echo

title "Tests (Python 3.5)"
./development/tests/run.sh 3.5
echo

title "Tests (Python 3.8)"
./development/tests/run.sh 3.8

title "Documentation"
./development/doc/build.sh

title "Demo"
./development/demo/run.sh

echo
echo "Development cycle OK"
