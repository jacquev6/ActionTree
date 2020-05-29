#!/bin/bash

set -o errexit


coverage erase
trap "coverage erase" EXIT

# Because of multiprocessing:
#   --branch option must be passed as rc file
#   --rcfile option must be passed as env variable
export COVERAGE_RCFILE=development/tests/coveragerc
coverage run -m unittest discover --pattern "*.py" --start-directory ActionTree --top-level-directory .
coverage combine

coverage html --directory="htmlcov/$(python --version)"

coverage report --skip-covered --fail-under=100

echo
echo "Detailed coverage report: htmlcov/$(python --version)/index.html"
echo
echo "Tests and coverage OK"
