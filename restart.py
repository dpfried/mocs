from os import getpid, kill
from signal import SIGINT

def restart():
    pid = getpid()
    kill(getpid(), SIGINT)
    return pid
