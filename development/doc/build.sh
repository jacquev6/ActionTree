#!/bin/bash

set -o errexit


image_id=$(
  docker build \
    --quiet \
    --file development/doc/Dockerfile \
    --tag action-tree-doc \
    .
)

docker run \
  --rm \
  --volume $PWD:/project \
  --workdir /project \
  action-tree-doc
