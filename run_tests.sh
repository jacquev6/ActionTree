#!/bin/sh

coverage erase

for f in *.test.py
do 
    coverage run --branch --append $f --quiet
done

coverage report -m --include="ActionTree.py"
