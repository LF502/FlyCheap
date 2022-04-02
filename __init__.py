from ctripcrawler import CtripCrawler, CtripSearcher, ItineraryCollector
from rebuilder import Rebuilder
import civilaviation
import sys as _sys
import time as _time

class Log():
    def __init__(self, logfile: str):
        self.terminal = _sys.stdout
        self.log = open(logfile, "a", encoding = 'UTF-8',)
 
    def write(self, message):
        self.terminal.write(message)
        if message.startswith("\n") or message.endswith("\n"):
            self.log.write("\n" + _time.strftime("%Y-%m-%d %H:%M:%S", _time.localtime()) + "\n")
        self.log.write(message)
    def flush(self):
        pass