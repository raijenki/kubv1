import time
import signal
import os
import sys
import subprocess
from multiprocessing import Process

STOP_TIMEOUT = 30
stream = None

def signal_handler(sig, _frame):
    """Handling the SIGTERM event"""
    print(f'Received signal {sig} - stopping gracefully in 30 seconds')
    stream.send_signal(sig)
    count = STOP_TIMEOUT
    while count > 30:
        time.sleep(1)
        count -= 1
    print('Finished cleanup...')
    

def main():
    """Opening subprocesses"""
    global stream
    stream = subprocess.Popen(["/home/stream_c"] + sys.argv[1:])
    signal.signal(signal.SIGTERM, signal_handler)
    stream.wait()
    print("Finish execution...")

if __name__ == "__main__":
    main()
