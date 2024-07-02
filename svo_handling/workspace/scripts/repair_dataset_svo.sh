#!/bin/bash

for file in dataset/*/zed2i.svo; do
printf "\n _______________________________________________________________________________\n"
    printf "Repairing $file"
    # repair the file with ZED_SVO_Editor
    ZED_SVO_Editor -repair "$file"

    # if $1 is --remove then remove the original file
    if [ "$1" == "--remove" ]; then
        printf "remove flag detected. Removing $file\n"
        rm "$file"
    fi

printf "\n _______________________________________________________________________________\n"
done
