# APEIRON post processing

This repo contains instructions and tools (mostly scripts, docker files and, python notebooks) to elaborate APEIRON data.<br>

## Overview

### Run or Flight session

APEIRON is divided in multiple **Run**s, each **run** is independent and contains all perception and network measurements of a single flight session. Each run is stored in a folder that can be downloaded from [here](https://c3lab.github.io/Apeiron/) using the **Download All** link.

### Run folder description

Each run contains different files related to different sensors/acquisition device. Here's an example folder structure:

- **event.bias:** bias settings employed to capture data from the  event-Based camera
- **event.raw.timestamp:** initial UNIX timestamp used as offset for the raw events, as events timestamp is relative to the initial boot of the camera
- **event*.raw:** event camera recording encoded in EVT3 format
- **zed2i*.svo:** stereocamera recordings with UNIX timestamp
- **log_*.ulg:** flight log, containing all the data captured by PixHawk’s sensors, such as GPS data, accelerometer, magnetometer, control inputs for the motors etc;
- **tcp-internals*.log:** output of ss (socket statistics) 
- **tcpdump-*.pcap:** packets capture
- **run.txt:** file containing meta data of the run (currently just run name)
- **exported_videos:** stereo camera videos exported from SVO file
    - RGB_left.avi
    - RGB_right.avi
    - depth_left.avi
- **px4_csvlogs:** folder containing px4 logs from the .ulg file exported in csv format (to ease the usability)
    - ***.csv:** various logs

## suggested path and symlink
In order to avoid problems with paths used by the scripts it is suggested to:
- Download the runs and put them in a folder named "dataset" in a path of your choice
- Create a symbolic link to that folder in the parent directory of this repository: `ln -s <PATH-TO-FOLDER>/dataset ../dataset_symlink`

**NOTE:** this dataset should be stored in a High Speed Memory support (such as an SSD) to avoid problems in the processing of the SVO files.


## Docker images
A set of docker images has been provided to facilitate installation of dependencies and the execution of provided scripts in a repeatable environment. 

### image to handle zed2i data (.SVO files) using Stereolab ZED SDK (NVIDIA-Docker required + Check ZED SDK hardware requirements)
#### build
navigate in svo_handling folder and build the docker image:<br>
`./build_docker.sh`
#### access the container
navigate in svo_handling folder and start a docker container:<br>
`./zed_docker_handler.sh`


### image to handle event camera data (.raw files) using OpenEB SDK
#### build
navigate in the event_raw_handling folder and build the docker image: <br>
`./build_docker.sh`
#### access the container
navigate in event_raw_handling folder and start a docker container:<br>
`./openeb_docker_handler.sh.sh`

### docker scripts

Some scripts which exploit docker images are provided as examples in the svo_handling and event_raw_handling folders. 

#### compute zed2i visual inertial odometry
navigate in svo_handling folder and start the script:<br>
`./auto_compute_tracking.sh`<br>
this script will compute visual inertial odometry using zed sdk tracking features for all the runs stored in the suggested path(see previous sections of this document)



## Jupyter Notebooks

In the `notebooks` folder you can find two notebooks:
- **GPS_VIO.ipynb:** Shows how to use zed_pose track results and px4 logs to compare the pose estimation **NOTE:**it is required to compute the zed2i visual inertial odometry tracking(check previous sections of this document).
- **post-processBW.ipynb:** Shows how to use the px4 position logs and socket statistics data to create a heatmap of the bandwidth.

## To Do
- provide a json file in each run with useful metadata
- document the **apeiron** python module used in the notebooks

