#!/bin/bash

for file in dataset/*/*.svo; do
printf "\n _______________________________________________________________________________\n"
    printf "Statistics of $file"
    # repair the file with ZED_SVO_Editor
    ZED_SVO_Editor -inf "$file"

    # file dimension in GB
    size=$(du -h "$file" | cut -f1)
    printf "Size: $size\n"


printf "\n _______________________________________________________________________________\n"
done
