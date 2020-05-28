#!/bin/bash

set -o errexit

./development/checks/run.sh
./development/tests/run.sh 3.5
./development/tests/run.sh 3.8
