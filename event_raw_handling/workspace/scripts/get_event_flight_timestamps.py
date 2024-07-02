import pandas as pd
import argparse

# get flight log path via argument
parser = argparse.ArgumentParser(description='Get flight timestamps from flight log')
parser.add_argument('flight_log', type=str, help='Path to flight log')

parser.add_argument('event_start_ts_file', type=str, help='Path to event start timestamp file')


# load flight log from csv

args = parser.parse_args()
flight_log_path = args.flight_log
flight_log = pd.read_csv(flight_log_path)

# get event start timestamps from first line of file that is like this: "Unix Timestamp: 1706885332"
event_start_ts_file = args.event_start_ts_file
with open(event_start_ts_file, 'r') as f:
    event_start_ts = int(f.readline().split(': ')[-1])
# get timestamps in nanoseconds

start_ts = (flight_log['time_utc_usec'].iloc[0]/1000000) - event_start_ts
end_ts = (flight_log['time_utc_usec'].iloc[-1]/1000000) - event_start_ts

print(start_ts)
print(end_ts)


