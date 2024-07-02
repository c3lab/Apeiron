#!/bin/bash

# IMAGE=zed-capture
IMAGE=zed_svo_handler:latest
echo $IMAGE

xhost +
docker run --rm -it --privileged --ipc host \
    --runtime nvidia --gpus all \
    -v /dev:/dev \
    -v ./workspace:/root/zed_workspace/ \
    -v ./zed_settings/:/usr/local/zed/settings/  \
    -v ${PWD}/../../dataset_symlink:/root/dataset \
    -e DISPLAY=$DISPLAY \
    -v /tmp/.X11-unix/:/tmp/.X11-unix \
    -v ~/.Xauthority:/root/.Xauthority \
    -e XAUTHORITY=/root/.Xauthority \
    -w /root/ \
    --name zed2i_svo_repair \
    $IMAGE ./zed_workspace/scripts/repair_dataset_svo.sh $1
