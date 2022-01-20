import datetime
import time


def timestamp_to_datetime(timestamp):
    if timestamp is None:
        return None
    return datetime.datetime.fromtimestamp(timestamp)
