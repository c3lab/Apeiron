########################################################################
#
# Copyright (c) 2022, STEREOLABS.
#
# All rights reserved.
#
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS
# "AS IS" AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT
# LIMITED TO, THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR
# A PARTICULAR PURPOSE ARE DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT
# OWNER OR CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL,
# SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT
# LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES; LOSS OF USE,
# DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON ANY
# THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT
# (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE
# OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.
#
########################################################################

import sys
import pyzed.sl as sl
import numpy as np
import cv2
from pathlib import Path
import enum
import argparse
import os 

class AppType(enum.Enum):
    LEFT_AND_RIGHT = 1
    LEFT_AND_DEPTH = 2
    LEFT_AND_DEPTH_16 = 3


def progress_bar(percent_done, bar_length=50):
    #Display a progress bar
    done_length = int(bar_length * percent_done / 100)
    bar = '=' * done_length + '-' * (bar_length - done_length)
    sys.stdout.write('[%s] %i%s\r' % (bar, percent_done, '%'))
    sys.stdout.flush()


def main():
    # Get input parameters
    svo_input_path = opt.input_svo_file
    avi_output_path_left = opt.output_avi_file_left
    avi_output_path_right = opt.output_avi_file_right
    avi_output_path_depth = opt.output_avi_file_depth
    output_as_video = True    

    # Specify SVO path parameter
    init_params = sl.InitParameters()
    init_params.set_from_svo_file(svo_input_path)
    init_params.svo_real_time_mode = False  # Don't convert in realtime
    init_params.coordinate_units = sl.UNIT.MILLIMETER  # Use milliliter units (for depth measurements)

    # Create ZED objects
    zed = sl.Camera()

    # Open the SVO file specified as a parameter
    err = zed.open(init_params)
    if err != sl.ERROR_CODE.SUCCESS:
        sys.stdout.write(repr(err))
        zed.close()
        exit()
    
    # Get image size
    image_size = zed.get_camera_information().camera_configuration.resolution
    width = image_size.width
    height = image_size.height
    
    # Prepare side by side image container equivalent to CV_8UC4
    svo_image_rgb_left = np.zeros((height, width, 4), dtype=np.uint8)
    svo_image_rgb_right = np.zeros((height, width, 4), dtype=np.uint8)
    svo_image_depth_left = np.zeros((height, width, 4), dtype=np.uint8)

    # Prepare single image containers
    left_image = sl.Mat()
    right_image = sl.Mat()
    depth_image = sl.Mat()

    video_writer = None
    if output_as_video:
        # Create video writer with MPEG-4 part 2 codec

        
        video_writer_left = cv2.VideoWriter(avi_output_path_left,
                                       cv2.VideoWriter_fourcc('M', '4', 'S', '2'),
                                       max(zed.get_camera_information().camera_configuration.fps, 25),
                                       (width, height))
        video_writer_right = cv2.VideoWriter(avi_output_path_right,
                                       cv2.VideoWriter_fourcc('M', '4', 'S', '2'),
                                       max(zed.get_camera_information().camera_configuration.fps, 25),
                                       (width, height))
        video_writer_depth = cv2.VideoWriter(avi_output_path_depth,
                                       cv2.VideoWriter_fourcc('M', '4', 'S', '2'),
                                       max(zed.get_camera_information().camera_configuration.fps, 25),
                                       (width, height))



        if not video_writer_left.isOpened():
            sys.stdout.write("OpenCV video writer left cannot be opened. Please check the .avi file path and write "
                             "permissions.\n")
            zed.close()
            exit()

        if not video_writer_right.isOpened():
            sys.stdout.write("OpenCV video writer right cannot be opened. Please check the .avi file path and write "
                             "permissions.\n")
            zed.close()
            exit()

        if not video_writer_depth.isOpened():
            sys.stdout.write("OpenCV video writer depth cannot be opened. Please check the .avi file path and write "
                             "permissions.\n")
            zed.close()
            exit()
        
    
    rt_param = sl.RuntimeParameters()

    # Start SVO conversion to AVI/SEQUENCE
    sys.stdout.write("Converting SVO... Use Ctrl-C to interrupt conversion.\n")

    nb_frames = zed.get_svo_number_of_frames()

    while True:
        err = zed.grab(rt_param)
        if err == sl.ERROR_CODE.SUCCESS:
            svo_position = zed.get_svo_position()

            # Retrieve SVO images
            zed.retrieve_image(left_image, sl.VIEW.LEFT)
            zed.retrieve_image(right_image, sl.VIEW.RIGHT)
            zed.retrieve_image(depth_image, sl.VIEW.DEPTH)


            if output_as_video:
                
                svo_image_rgb_left= left_image.get_data()

                svo_image_rgb_right = right_image.get_data()

                svo_image_depth_left = depth_image.get_data()
                
                # convert from RGBA to RGB
                ocv_image_rgb_left = cv2.cvtColor(svo_image_rgb_left, cv2.COLOR_RGBA2RGB)
                ocv_image_rgb_right = cv2.cvtColor(svo_image_rgb_right, cv2.COLOR_RGBA2RGB)
                ocv_image_rgb_depth = cv2.cvtColor(svo_image_depth_left, cv2.COLOR_RGBA2RGB)

                # Write the RGB image in the videos
                video_writer_left.write(ocv_image_rgb_left)
                video_writer_right.write(ocv_image_rgb_right)
                video_writer_depth.write(ocv_image_rgb_depth)
                
            # Display progress
            progress_bar((svo_position + 1) / nb_frames * 100, 30)
        if err == sl.ERROR_CODE.END_OF_SVOFILE_REACHED:
            progress_bar(100 , 30)
            sys.stdout.write("\nSVO end has been reached. Exiting now.\n")
            break
    if output_as_video:
        # Close the video writer
        video_writer_left.release()
        video_writer_right.release()
        video_writer_depth.release()

    zed.close()
    return 0


if __name__ == "__main__":
    parser = argparse.ArgumentParser(formatter_class=argparse.RawTextHelpFormatter)
    parser.add_argument('--input_svo_file', type=str, required=True, help='Path to the .svo file')
    parser.add_argument('--output_avi_file_depth', type=str, help='Path to the output .avi file, if mode includes a .avi export', default = '')
    parser.add_argument('--output_avi_file_right', type=str, help='Path to the output .avi file, if mode includes a .avi export', default = '')
    parser.add_argument('--output_avi_file_left', type=str, help='Path to the output .avi file, if mode includes a .avi export', default = '')
  
    opt = parser.parse_args()

    main()