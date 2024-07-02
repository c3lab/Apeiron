
IMAGE=openeb_event_raw_handler

echo $IMAGE


xhost +
docker run --rm -it --privileged -e DISPLAY --net host  --ipc host \
    -v /tmp/.X11-unix:/tmp/.X11-unix \
    -v="$HOME/.Xauthority:/root/.Xauthority:rw" \
    -e XAUTHORITY=/root/.Xauthority\
    -e DISPLAY=$DISPLAY \
    -v ./workspace:/root/eb_workspace/ \
    -v ${PWD}/../../dataset_symlink:/root/dataset \
    -w /root/\
    --name event_raw_handler \
    $IMAGE bash
