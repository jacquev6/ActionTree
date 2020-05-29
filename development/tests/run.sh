#!/bin/bash

set -o errexit


python_version=$1

if [ -z "$python_version" ]
then
  echo "Usage: ./development/tests/run.sh python_version"
  exit 1
fi

image_id=$(
  docker build \
    --quiet \
    --file development/tests/Dockerfile \
    --build-arg python_version=$python_version \
    --tag action-tree-tests:$python_version \
    .
)

docker run \
  --rm \
  --volume $PWD:/project \
  --workdir /project \
  $image_id
