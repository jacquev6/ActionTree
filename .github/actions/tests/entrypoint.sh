#!/bin/bash

set -o errexit


pip install .[dependency_graphs,gantt]

python setup.py test --quiet
