#!/bin/bash

set -o errexit

# @todo Reduce verbosity (too much noise)
# @todo Build docs

./development/checks/run.sh
./development/tests/run.sh 3.5
./development/tests/run.sh 3.8
