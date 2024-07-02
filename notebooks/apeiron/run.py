from enum import Enum
import pandas as pd 
import os
from glob import glob
from .net import TcpInternals
from pyproj import Transformer
import numpy as np


"""
The Scenario enum is used to define the scenario of the run.
"""
class Scenario(Enum):
    OPEN_FIELD = 1,
    INDUSTRIAL = 2,

transformer = Transformer.from_crs("WGS84", "EPSG:3003")

"""
The method converts latitude and longitude to the x and y coordinates in the EPSG:3003 coordinate system
"""
def convert_latlon_to_xy(lat, lon):
    x, y = transformer.transform(lon/1e7, lat/1e7)
    return x, y

class Run:
    """
    The runs of the dataset are organized this way:
        dataset/: dataset path
            run-DD-MM-YYYY-hh-mm-ss/: run's logs path
                tcp-internals.log: TCP internals logs if the net direction is uplink
                tcp-internals-down.log: TCP internals logs if the net direction is downlink
                run.txt: contains run's metadata
                log_NN_YYYY-DD-MM-hh-mm-ss_global_position_0.csv: PX4 CSV file containing global position information 
    
    NOTICE: a single run can contain multiple logs, but only one TCP internals log. The "direction" of the TCP
    connection is determined by the filename. The direction can be automatically determined by looking at which file is present in
    the run's directory. If a file name "tcp-internals.log" is present, the direction is "up". If a file named "tcp-internals-down.log"
    is present, the direction is "down".
    """
    def __init__(self, run_directory, scenario):
        self.run_directory = run_directory
        self.direction = self.log_direction()
        self.scenario = scenario
        filename = "tcp-internals.log" if self.direction == "up" else "tcp-internals-down.log"
        self.tcp_internals = TcpInternals(self.direction, filename=os.path.join(self.run_directory, filename))
        self.run_metadata = self.parse_run_metadata()
        print(os.path.join(self.run_directory,"px4_csvlogs/*vehicle_local_position_0.csv"))
        self.df_px4pos = pd.read_csv(glob(os.path.join(self.run_directory,"px4_csvlogs/*vehicle_local_position_0.csv"))[0])
        self.df_gps_utc = pd.read_csv(glob(os.path.join(self.run_directory,"px4_csvlogs/*vehicle_gps_position_0.csv"))[0])
        self.time_utc_offset = self.df_gps_utc['time_utc_usec'][0] - self.df_gps_utc['timestamp'][0]

        tcp_df = self.tcp_internals.df
        gps_df = self.df_gps_utc
        gps_df['ts'] = pd.to_datetime(gps_df.time_utc_usec/1e6, unit="s")
        tcp_df['ts'] = pd.to_datetime(tcp_df['timestamp'], unit = "s")

        # Merge the two dataframes
        gps_df = gps_df.sort_values('ts')
        tcp_df = tcp_df.sort_values('ts')
        self.merged_df = pd.merge_asof(gps_df, tcp_df, on='ts', direction='nearest', tolerance=pd.Timedelta('0.2s'))
        self.compute_throughput()

    """
    The method computes the throughput of the TCP connection
    """
    def compute_throughput(self):
        merged_df = self.merged_df
        merged_df['x'], merged_df['y'] = zip(*merged_df.apply(lambda row: convert_latlon_to_xy(row['lat'], row['lon']), axis=1))
        merged_df['x'] = merged_df['x'] - merged_df['x'].min()
        merged_df['y'] = merged_df['y'] - merged_df['y'].min()

        merged_df['bytes_diff'] = merged_df['bytes_sent'].diff()
        merged_df['time_diff'] = merged_df['ts'].diff().dt.total_seconds()

        # Calculate the throughput
        merged_df['throughput'] = merged_df['bytes_diff'] / merged_df['time_diff'] * 8 / 1e6 # Mbps

        # Fill NaN values with 0
        merged_df['throughput'] = merged_df['throughput'].fillna(0)
        self.merged_df = merged_df

    """
    The method returns the direction of the TCP connection

    """
    def log_direction(self):
        if os.path.isfile(os.path.join(self.run_directory, "tcp-internals.log")):
            return "up"
        elif os.path.isfile(os.path.join(self.run_directory, "tcp-internals-down.log")):
            return "down"
        else:
            return "Unknown"
        
    """
    The method returns the scenario enum of the run based on the run's metadata
    """    
    def identify_scenario(self):
        pass
        
        
    """
    TODO: instead of run.txt we should have JSON file run.json holding the metadata
    """
    def parse_run_metadata(self):
        run_metadata = {}
        with open(os.path.join(self.run_directory, "run.txt"), "r") as f:
            run_metadata = f.read()
        return run_metadata
    

    """
    The method computes the bandwidth grid (BW) in an NxN grid. 
    Input:
    - N: the number of cells in the grid both in the x and y axis
    Output:
    - x_grid: the x-axis grid
    - y_grid: the y-axis grid
    - BW: an (N-1)x(N-1) matrix collecting the bandwidth computed in each cell of the grid
    """
    def compute_bw_xy(self, N):
        merged_df = self.merged_df
        x_grid = np.linspace(0, merged_df['x'].max(), N)
        y_grid = np.linspace(0, merged_df['y'].max(), N)
        sum_samples = 0
        BW = np.zeros((len(x_grid)-1, len(y_grid)-1))
        for i in range(0, len(x_grid)-1):    
            for j in range(0, len(y_grid)-1):                
                cut = merged_df[ (merged_df['x'].between(x_grid[i],x_grid[i+1], inclusive='both')) & ( merged_df['y'].between(y_grid[j],y_grid[j+1], inclusive='both'))]
                sum_samples += len(cut)
                BW[i,j] = cut.throughput.mean()

        return x_grid, y_grid, BW 