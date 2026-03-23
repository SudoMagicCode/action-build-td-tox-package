'''
A small log handling utility library
'''
import os
from datetime import datetime


def log_event(msg: str, indent: int = 0) -> None:
    print(f"{datetime.now()} | {'--' * indent}> {msg}")


def write_log_to_cloud(log_path: str) -> None:
    '''A function that reads out the lines of a log file one at a time so it can be shared with the cloud
    '''
    try:
        with open(log_path, 'r') as target_file:
            for line in target_file:
                # Print each line
                print(f"--> {line.strip()}")

        # deletes file after reading it
        print(f"--> Cleaning up log")
        os.remove(log_path)
    except Exception as e:
        print("NO TD Log file present")
