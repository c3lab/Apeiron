#!/bin/bash

number_of_runs=$(ls -d dataset/*run*/ | wc -l)
counter=0
for path in dataset/*run*/; do

    counter=$((counter+1))

    printf "\n _______________________________________________________________________________\n"
    printf "Processing $path\n"
    printf "Run $counter of $number_of_runs\n"

    svo_file=$path"zed2i_repaired.svo"
    #px4_gps_utc_log=$path"px4_csvlogs/*vehicle_gps_position_0.csv"
    px4_gps_utc_log=$(ls $path/px4_csvlogs/*vehicle_gps_position_0.csv)
    printf "$svo_file\n"
    printf "$px4_gps_utc_log\n"

    # if file does not exist, skip
    if [ ! -f "$svo_file" ] || [ ! -f "$px4_gps_utc_log" ]; then

        # print "skipping" in red with printf
        printf "\e[31mrepaired.svo or px4_csvlogs/*vehicle_gps_position_0.csv does not exist. Skipping.\n\e[0m\n"
        printf "This is not an error message, just a warning. If there are other runs to process, I will keep going forward, tatakae!.\n"
        
        printf "\n _______________________________________________________________________________\n"
        continue
    fi

    # get start and end timestamps in nanoseconds
    start_ts=$(python3 zed_workspace/scripts/get_svo_flight_timestamps.py "$px4_gps_utc_log" | sed -n "1p")
    end_ts=$(python3 zed_workspace/scripts/get_svo_flight_timestamps.py "$px4_gps_utc_log" | sed -n "2p")

    printf "Cutting $svo_file from $start_ts to $end_ts\n"
    # print duration in minutes and seconds
    duration=$(echo "($end_ts - $start_ts) / 1000000000" | bc)
    minutes=$(echo "$duration / 60" | bc)
    seconds=$(echo "$duration % 60" | bc)
    printf "Duration: $minutes minutes and $seconds seconds\n"

    # cut the file with ZED_SVO_Editor
    ZED_SVO_Editor -cut $svo_file -start-timestamp $start_ts -end-timestamp $end_ts $path"zed2i_px4_aligned.svo"

    # if $1 is --remove then remove the original file
    if [ "$1" == "--remove" ]; then
        printf "remove flag detected. Removing $svo_file\n"
        rm $svo_file
    fi
    printf "\n _______________________________________________________________________________\n"
    printf "\n"
done

