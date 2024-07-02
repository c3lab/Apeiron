import numpy as np
import pandas as pd
from glob import glob
import os

# Description: This file contains the implementation of the TcpInternals class,
# which is used to parse and analyze TCP internals data.

class TcpInternals:
    """
        Initializes an instance of TcpInternals.

        Parameters:
        - direction (str): The direction of the TCP connection ('up' or 'down').
        - filename (str): The name of the log file containing TCP internals data.
                          Default is 'tcp-internals.log'.
    """
    def __init__(self, direction, filename='tcp-internals'):
        self.lines = open(filename, 'r').readlines()
        
        # Validate the direction input
        if direction in ['up','down']:
            self.direction = direction
        else:
            raise ValueError("Direction must be 'up' or 'down'.")
        if self.direction == 'down':
            peer_dir = 'peer'
        else:
            peer_dir = 'local'
        self.df = pd.read_csv(filename, sep = "\s+|\t+|\s+\t+|\t+\s+")
        df_tmp = self.df[[peer_dir,'bytes_sent']]
        peer_tcp = df_tmp.groupby(peer_dir).max()['bytes_sent'].idxmax()
        self.df = self.df[self.df[peer_dir]== peer_tcp].reset_index() 
        self.df[['rtt_val', 'rtt_var']] = self.df['rtt'].str.split('/', expand=True)
        self.df['rtt_val'] = self.df['rtt_val'].astype(float)
        self.df['rtt_var'] = self.df['rtt_var'].astype(float)

        #self.avg_metrics()

    """
    Computes the throughput of the TCP connection.
    """
    def compute_throughput(self):
        t = pd.to_datetime(self.df.timestamp, unit="s")
        sent = pd.Series(data=self.df.bytes_sent.to_numpy(), index=t).resample("1s").max().ffill()
        return sent.diff() / sent.index.to_series().diff().dt.total_seconds()
        
    
    def avg_metrics(self):
        """
        Calculates average metrics based on parsed data.

        Returns:
        - avg (dict): A dictionary containing average TCP metrics.
        'duration'    duration of the experiment in seconds
        'rtt'         average RTT measured in ms
        'rtt_min'     minimum measured RTT
        'goodput'     average goodput measured in bps
        'loss_ratio'  Average loss ratio
        'mss'         The maximum segment size
        'dir'         Direction ('down' for downlink, 'up' for uplink)
        """
        
        avg = dict()
        df = self.df
        df = df[df['bytes_sent'].notna()].reset_index() 
        N = len(df) - 1
        
        dur = df['timestamp'][N] - df['timestamp'][0]
        avg['duration'] = dur # in sec
        bytes = df['bytes_sent'] # - df['bytes_retrans'] # Good bytes
        avg['rtt'] = df['rtt_val'].mean(axis=0) # in ms
        avg['goodput'] = bytes[N]/(dur)*8.0/1e6 # in bps
        avg['loss_ratio'] = df['bytes_retrans'][N]/df['bytes_sent'][N]
        avg['rtt_min'] = df['minrtt'][N] # in ms
        avg['mss'] = df['mss'][N]
        avg['dir'] = self.direction
        self.average = avg
        return avg

    def get_average(self):
        """
        Returns the calculated average metrics.

        Returns:
        - average (dict): A dictionary containing average TCP metrics.
        """
        return self.average

    def get_dataframe(self):
        """
        Returns the DataFrame containing parsed TCP metrics.

        Returns:
        - df (pd.DataFrame): Pandas DataFrame with TCP metrics.
        """
        return self.df
        
class UlgParse:

    def __init__(self, filename):
        self.filename = filename
        self.df = pd.read_csv(filename)

class TcpDataset:
    """
    
    """
    def __init__(self, directory='../samples/'):

        (rate_up, dataset_up, ulg_up) = self.create_dataframe(directory, 'up')   
        (rate_down, dataset_down, ulg_down) = self.create_dataframe(directory, 'down')
        self.rate = pd.concat([rate_up,rate_down])
        self.dataset = pd.concat([dataset_up, dataset_down])
        self.ulg = pd.concat([ulg_up,ulg_down])
        


    def create_dataframe(self, directory, direction):
        if direction == 'up':
            filter = directory + '*/tcp-internals.log'
            dirstr = 'Uplink'
        else:
            dirstr = 'Downlink'
            filter = directory + '*/tcp-internals-down.log'
        
        runs = glob(filter, recursive = True)
        rate_df = pd.DataFrame()
        dataset = pd.DataFrame()
        ulg_df = pd.DataFrame()
        for r in runs:
            try:
                basedir = os.path.dirname(r)
                
                run_fname = os.path.join(basedir,'run.txt')
                run_idx = open(run_fname, 'r').readlines()[0].strip()
                print('run index', run_idx, 'filename', r)
                t = TcpInternals(direction, filename=r)
                print(t.avg_metrics())
                rate = t.compute_throughput().to_frame(name='rate')
                rate['rate'] = rate['rate']*8/1e6
                rate['direction'] = dirstr
                rate['run'] = run_idx
                rate = rate[rate['rate'].notna()].reset_index() 
                rate_df = pd.concat([rate_df, rate])

                t.df['direction'] = dirstr
                t.df['run'] = run_idx
                dataset = pd.concat([dataset, t.df])

                gps = glob(basedir + '/log_*vehicle_gps_position*.csv')[0]
                ulg = UlgParse(gps)
                ulg.df['direction'] = dirstr
                ulg.df['run'] = run_idx
                
                ulg_df = pd.concat([ulg_df, ulg.df])
            except:
                print('Run ', r, 'is bugged')
                
        return [rate_df,dataset, ulg_df]
    
