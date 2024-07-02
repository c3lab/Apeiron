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

import pyzed.sl as sl
import sys

def main():
    # Create a Camera object
    
    
    # get name from argument
    if len(sys.argv) > 2:
        input_path = sys.argv[1]
        out_path = sys.argv[2]
    else:
        print("Missing arguments - Usage: python3 posetrack.py <input_path> <out_path>")
        exit()
        

    zed = sl.Camera()

    # Create a InitParameters object and set configuration parameters
    init_params = sl.InitParameters()
    init_params.camera_resolution = sl.RESOLUTION.AUTO # Use HD720 or HD1200 video mode (default fps: 60)
    init_params.coordinate_system = sl.COORDINATE_SYSTEM.RIGHT_HANDED_Y_UP # Use a right-handed Y-up coordinate system
    init_params.coordinate_units = sl.UNIT.METER  # Set units in meters

    # get input from SVO file
    init_params.set_from_svo_file(input_path)

    # Open the camera
    err = zed.open(init_params)
    if err != sl.ERROR_CODE.SUCCESS:
        print("Camera Open : "+repr(err)+". Exit program.")
        exit()


    # Enable positional tracking with default parameters
    py_transform = sl.Transform()  # First create a Transform object for TrackingParameters object
    tracking_parameters = sl.PositionalTrackingParameters(_init_pos=py_transform)
    err = zed.enable_positional_tracking(tracking_parameters)
    if err != sl.ERROR_CODE.SUCCESS:
        print("Enable positional tracking : "+repr(err)+". Exit program.")
        zed.close()
        exit()

    # Track the camera position during 1000 frames
    i = 0
    zed_pose = sl.Pose()

    zed_sensors = sl.SensorsData()
    runtime_parameters = sl.RuntimeParameters()
    
    can_compute_imu = zed.get_camera_information().camera_model != sl.MODEL.ZED
    # get SVO number of frames
    num_frames = zed.get_svo_number_of_frames()

    error_code = sl.ERROR_CODE.SUCCESS
    # iterate until zed svo file is finished
    with open(out_path, 'w') as f:
        while error_code == sl.ERROR_CODE.SUCCESS:

            error_code = zed.grab(runtime_parameters)
            if error_code== sl.ERROR_CODE.SUCCESS:
                # Get the pose of the left eye of the camera with reference to the world frame
                zed.get_position(zed_pose, sl.REFERENCE_FRAME.WORLD)
                
                # Display the translation and timestamp
                py_translation = sl.Translation()
                tx = round(zed_pose.get_translation(py_translation).get()[0], 3)
                ty = round(zed_pose.get_translation(py_translation).get()[1], 3)
                tz = round(zed_pose.get_translation(py_translation).get()[2], 3)
                # use \r to overwrite the line
                

                # save in a csv file named out_path
                
                f.write(str(tx) + "," + str(ty) + "," + str(tz) + "," + str(zed_pose.timestamp.get_milliseconds()) + "\n")

                i = i + 1
                # print using 3 decimal places
                #print("Translation: Tx: {0:.3f}, Ty: {1:.3f}, Tz {2:.3f}, Timestamp: {3}   Frame {4:05d}/{5:05d}".format(tx, ty, tz, zed_pose.timestamp.get_milliseconds(), i, num_frames), end='\n')
                print("Frame {4:05d}/{5:05d}".format(tx, ty, tz, zed_pose.timestamp.get_milliseconds(), i, num_frames), end='\r')
            
        
    # Close the camera
    zed.close()

    print("\nFINISH")

if __name__ == "__main__":
    main()