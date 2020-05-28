#!/bin/sh

set -o errexit

# @todo Measure coverage, generate HTML report
python -m unittest discover --pattern "*.py" --start-directory ActionTree --top-level-directory .
