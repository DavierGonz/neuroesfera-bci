import time

def wait(seconds):

    start = time.time()

    while time.time() - start < seconds:
        pass