#!/bin/bash

number_of_runs=$(ls -d dataset/*run*/ | wc -l)
counter=0

for path in dataset/*run*/; do
    counter=$((counter+1))

    printf "\n _______________________________________________________________________________\n"
    printf "Processing $path\n"
    printf "Run $counter of $number_of_runs\n"    
    svo_file=$path"*.svo"

    # get file name evaluating *
    svo_file=$(ls $svo_file)

    printf "$svo_file\n"
   
    # if file does not exist, skip
    if [ ! -f "$svo_file" ]; then

        # print "skipping" in red with printf
        printf "\e[31mzed2i_px4_aligned.svo does not exist. Skipping.\n\e[0m\n"
        printf "This is not an error message, just a warning. If there are other runs to process, I will keep going forward, tatakae!\n"
        
        printf "\n _______________________________________________________________________________\n"
        continue
    fi

    # create folder for exported videos
    mkdir -p $path/exported_videos

    # cut the file with ZED_SVO_Editor
    python3 zed_workspace/export_videos.py --input_svo_file $svo_file --output_avi_file_depth $path/exported_videos/depth_left.avi --output_avi_file_right $path/exported_videos/RGB_right.avi --output_avi_file_left $path/exported_videos/RGB_left.avi
    printf "\n _______________________________________________________________________________\n"
    printf "\n"
done

