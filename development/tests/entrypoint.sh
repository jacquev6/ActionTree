#!/bin/sh

set -o errexit

# @todo Measure coverage, generate HTML report
python setup.py test --quiet
