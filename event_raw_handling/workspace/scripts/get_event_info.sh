#!/bin/bash

for file in dataset/*/*.raw; do
	printf "\n _______________________________________________________________________________\n"
    printf "Statistics of $file"
	metavision_file_info -i "$file"

	# output file dimension in GB
	size=$(du -h "$file" | cut -f1)
	printf "Size: $size\n"

	printf "\n _______________________________________________________________________________\n"
done
