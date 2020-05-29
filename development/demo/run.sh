#!/bin/bash

set -o errexit


image_id=$(
  docker build \
    --quiet \
    --file development/demo/Dockerfile \
    --tag action-tree-demo \
    .
)

docker run \
  --rm \
  --volume $PWD:/project \
  --workdir /project \
  action-tree-demo
