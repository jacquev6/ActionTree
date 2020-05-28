#!/bin/bash

set -o errexit

./development/tests/run.sh 3.5
./development/tests/run.sh 3.8
