#!/bin/sh

set -o errexit


docker build \
  --file development/checks/Dockerfile \
  --tag action-tree-checks \
  .

docker run \
  --rm \
  --volume $PWD:/project \
  --workdir /project \
  action-tree-checks
