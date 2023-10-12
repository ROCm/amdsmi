#!/usr/bin/env bash

# this program generates py-interface/amdsmi_wrapper.py

set -eu

# get current dir
DIR=$( cd -- "$( dirname -- "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )

# override by calling this script with:
# DOCKER_NAME=yourdockername ./update_wrapper.sh
DOCKER_NAME="${DOCKER_NAME:-dmitriigalantsev/amdsmi_wrapper_updater}"

command -v docker &>/dev/null || {
    echo "Please install docker!" >&2
    exit 1
}

does_image_exist () {
    docker images | grep -q "$DOCKER_NAME"
}

if ! does_image_exist; then
    # if you prefer to not generate it yourself:
    # pull from https://hub.docker.com/r/dmitriigalantsev/amdsmi_wrapper_updater
    # using the following command:
    # docker pull dmitriigalantsev/amdsmi_wrapper_updater
    echo "No docker image found! Generating one"
    # set to 0 because it's compatible with more systems
    DOCKER_BUILDKIT="${DOCKER_BUILDKIT:0}" docker build "$DIR/py-interface" -t "$DOCKER_NAME":latest
fi

docker run --rm -ti --volume "$DIR":/src:rw "$DOCKER_NAME":latest

echo -e "Generated new wrapper!
[$DIR/py-interface/amdsmi_wrapper.py]"
