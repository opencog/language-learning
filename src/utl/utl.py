import time, datetime

def UTC():
    return str(datetime.datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S UTC'))
