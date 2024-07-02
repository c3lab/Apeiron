import pandas as pd
import argparse

# get flight log path via argument
parser = argparse.ArgumentParser(description='Get flight timestamps from flight log')
parser.add_argument('flight_log', type=str, help='Path to flight log')

# load flight log from csv

args = parser.parse_args()
flight_log_path = args.flight_log
flight_log = pd.read_csv(flight_log_path)

# get timestamps in nanoseconds

start_ts = flight_log['time_utc_usec'].iloc[0]*1000
end_ts = flight_log['time_utc_usec'].iloc[-1]*1000

print(start_ts)
print(end_ts)


