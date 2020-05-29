#!/bin/bash

set -o errexit


image_id=$(
  docker build \
    --quiet \
    --file development/checks/Dockerfile \
    --tag action-tree-checks \
    .
)

docker run \
  --rm \
  --volume $PWD:/project \
  --workdir /project \
  action-tree-checks
